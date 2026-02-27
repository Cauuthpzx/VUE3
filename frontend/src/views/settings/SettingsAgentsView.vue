<script setup>
import { onMounted, onUnmounted, nextTick, ref, computed, watch } from 'vue'
import { agentsApi } from '@/api/agents'
import { useAuthStore } from '@/stores/auth'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { initDateRange } from '@/composables/useLayuiDate'
import { useI18n } from '@/composables/useI18n'

const { t, locale } = useI18n()
const numLocale = { vi: 'vi-VN', en: 'en-US', 'zh-CN': 'zh-CN' }
const authStore = useAuthStore()
const { createTemplate } = useLayuiTemplate()

/* ===== STATE ===== */
const agents = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingAgent = ref(null)
const loginLoading = ref({})
const checkLoading = ref({})
const agentLocks = ref({}) // per-agent operation lock to prevent duplicate ops

const form = ref({ owner: '', username: '', base_url: '', password: '' })
const formError = ref('')

const agentSync = ref({})
const globalSyncing = ref(false)
const syncLog = ref([])
const syncDate = ref('')

let wsMap = {}
let treeTableReady = false
let tipsIndex = null
let fetchDebounceTimer = null

const allEndpoints = [
  { key: 'members', label: t('settings.epMembers') },
  { key: 'invites', label: t('settings.epInvites') },
  { key: 'bets', label: t('settings.epBets') },
  { key: 'bet_third_party', label: t('settings.epBetThirdParty') },
  { key: 'deposits', label: t('settings.epDeposits') },
  { key: 'withdrawals', label: t('settings.epWithdrawals') },
  { key: 'report_lottery', label: t('settings.epReportLottery') },
  { key: 'report_funds', label: t('settings.epReportFunds') },
  { key: 'report_provider', label: t('settings.epReportProvider') },
]

/* ===== COMPUTED ===== */
const globalStatus = computed(() => {
  if (globalSyncing.value) return 'syncing'
  const syncs = Object.values(agentSync.value)
  if (syncs.length === 0) return 'idle'
  if (syncs.some(s => s.status === 'error')) return 'error'
  if (syncs.some(s => s.status === 'done')) return 'done'
  return 'idle'
})

const globalStatusLabel = computed(() => {
  const map = { idle: '', syncing: t('settings.syncing'), done: t('settings.syncDone'), error: t('settings.syncError') }
  return map[globalStatus.value] || ''
})

const syncableAgents = computed(() => agents.value.filter(a => a.cookie_set))

/* ===== BUILD TREE DATA FOR LAYUI ===== */
function buildTreeData() {
  return agents.value.map(agent => {
    const state = agentSync.value[agent.id]
    const status = state?.status || 'idle'
    const cookieStatus = agent.cookie_status || 'none'
    const cookieMap = { none: t('settings.cookieNone'), unknown: t('settings.cookieUnknown'), valid: t('settings.cookieValid'), expired: t('settings.cookieExpired') }
    const syncMap = { idle: t('settings.syncIdle'), syncing: t('settings.syncSyncing'), done: t('settings.syncDone'), error: t('settings.epError') }

    const progressPct = (state && state.progress.total) ? Math.round((state.progress.done / state.progress.total) * 100) : 0
    const progressText = (state && state.progress.total) ? state.progress.done + '/' + state.progress.total : ''
    const totalRows = (state && (state.totalRows > 0 || status === 'done')) ? state.totalRows.toLocaleString(numLocale[locale.value] || 'vi-VN') : '-'
    const errCount = state ? Object.values(state.results || {}).filter(r => r?.error).length : 0
    const lastSync = state?.lastSyncAt || '-'

    const children = allEndpoints.map(ep => {
      const r = state?.results[ep.key] || null
      const detail = state?.detailStatus[ep.key] || ''
      const vr = state?.verifyResults[ep.key] || null
      let epStatus = 'idle', epLabel = '-'
      if (r) {
        if (r.error) { epStatus = 'error'; epLabel = t('settings.epError') }
        else if (r.skipped) { epStatus = 'skip'; epLabel = t('settings.epSkip') }
        else { epStatus = 'done'; epLabel = t('settings.epOk') }
      } else if (detail) { epStatus = 'syncing'; epLabel = t('settings.epSyncing') }

      // Add lock icon if verified/locked
      let lockIcon = ''
      if (vr) {
        if (vr.status === 'locked') lockIcon = ' <span class="tt-lock" title="🔒 ' + t('settings.lockedDays', { count: vr.locked_count }) + '">🔒</span>'
        else if (vr.status === 'mismatch') lockIcon = ' <span class="tt-lock-warn" title="⚠ ' + t('settings.dataMismatch') + '">⚠</span>'
      }
      if (r?.locked_count > 0) {
        lockIcon = ' <span class="tt-lock" title="🔒 ' + t('settings.skippedLockedDays', { count: r.locked_count }) + '">🔒</span>'
      }

      const epRows = (r && !r.error && !r.skipped) ? (r.fetched || 0).toLocaleString(numLocale[locale.value] || 'vi-VN') : '-'
      const epSaved = (r && !r.error && !r.skipped) ? (r.saved || 0).toLocaleString(numLocale[locale.value] || 'vi-VN') : '-'
      let epNote = ''
      if (!r) epNote = detail
      else if (r.error) epNote = r.error
      else if (r.skipped) epNote = r.reason || ''

      return {
        id: agent.id + '_' + ep.key,
        _isChild: true,
        name: ep.label + lockIcon,
        cookie: '',
        syncStatus: '<span class="tt-status tt-status--' + epStatus + '">' + epLabel + '</span>',
        progress: epNote ? '<span class="tt-note" title="' + epNote.replace(/"/g, '&quot;') + '">' + epNote + '</span>' : '',
        rows: epRows,
        saved: epSaved,
        time: '',
      }
    })

    return {
      id: agent.id,
      _isAgent: true,
      _agentData: JSON.stringify({
        id: agent.id,
        owner: agent.owner,
        username: agent.username,
        base_url: agent.base_url,
        cookie_set: agent.cookie_set,
        password_set: agent.password_set,
        cookie_status: cookieStatus,
      }),
      _syncStatus: status,
      name: '<strong>' + agent.owner + '</strong> <span class="tt-sub">' + agent.username + '</span>',
      cookie: '<span class="tt-cookie tt-cookie--' + cookieStatus + '">' + (cookieMap[cookieStatus] || cookieStatus) + '</span>',
      syncStatus: '<span class="tt-status tt-status--' + status + '">' + (syncMap[status] || t('settings.syncIdle')) + '</span>',
      progress: status !== 'idle'
        ? '<div class="tt-bar"><div class="tt-bar-fill tt-fill--' + status + '" style="width:' + progressPct + '%"></div>' + (progressText ? '<span class="tt-bar-text">' + progressText + '</span>' : '') + '</div>'
        : '',
      rows: totalRows,
      saved: errCount > 0 ? '<span class="tt-err">' + errCount + ' ' + t('settings.errors') + '</span>' : '',
      time: lastSync,
      children: children,
    }
  })
}

/* ===== RENDER TREE TABLE ===== */
function renderTreeTable() {
  nextTick(() => {
    layui.use(['treeTable'], (treeTable) => {
      const oldView = document.querySelector('.layui-table-view[lay-id="agentTree"]')
      if (oldView) oldView.remove()

      treeTable.render({
        elem: '#agentTreeTable',
        id: 'agentTree',
        data: buildTreeData(),
        tree: {
          customName: { children: 'children' },
          view: { showIcon: false },
        },
        toolbar: '#tplAgentToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        escape: false,
        cols: [[
          { field: 'name', title: t('settings.agentEndpoint'), width: 180, fixed: 'left' },
          { field: 'cookie', title: t('settings.cookie'), width: 110, fixed: 'left' },
          { field: 'syncStatus', title: t('settings.sync'), width: 110 },
          { field: 'progress', title: t('settings.progress'), minWidth: 150 },
          { field: 'rows', title: t('settings.rows'), width: 80, align: 'right', style: 'font-family:Consolas,monospace;font-weight:600' },
          { field: 'saved', title: t('settings.errorSaved'), width: 90, align: 'right', style: 'font-family:Consolas,monospace;font-weight:600' },
          { field: 'time', title: t('settings.at'), width: 90, style: 'color:#999;font-size:11px' },
          { title: t('common.actions'), width: 250, align: 'center', fixed: 'right', toolbar: '#tplAgentRowBar' },
        ]],
        skin: 'grid',
        even: true,
        size: 'sm',
        page: false,
        text: { none: t('settings.noAgentYet') },
      })

      treeTableReady = true
      nextTick(() => setupTableTips())

      treeTable.on('toolbar(agentTree)', (obj) => {
        switch (obj.event) {
          case 'syncAll': syncAll(); break
          case 'loginAll': loginAllAgents(); break
          case 'checkAll': checkAllCookies(); break
          case 'addAgent': openAdd(); break
          case 'clearResults': clearAllSync(); break
        }
      })

      treeTable.on('tool(agentTree)', (obj) => {
        if (!obj.data._isAgent) return
        let agent
        try { agent = JSON.parse(obj.data._agentData) } catch { return }

        switch (obj.event) {
          case 'syncAgent': syncAgent(agent); break
          case 'stopSync': stopSync(agent); break
          case 'loginAgent': loginAgent(agent); break
          case 'checkCookie': checkCookie(agent); break
          case 'editAgent': openEdit(agent); break
          case 'deleteAgent': deleteAgent(agent); break
          case 'clearData': clearAgentData(agent); break
        }
      })
    })
  })
}

function reloadTreeData() {
  if (!treeTableReady) return
  layui.use(['treeTable'], (treeTable) => {
    treeTable.reload('agentTree', { data: buildTreeData() })
  })
}

/* ===== HELPERS: LOCK & DEBOUNCE ===== */
function isAgentLocked(agentId, operation) {
  return !!agentLocks.value[agentId + ':' + operation]
}

function lockAgent(agentId, operation) {
  agentLocks.value[agentId + ':' + operation] = true
}

function unlockAgent(agentId, operation) {
  delete agentLocks.value[agentId + ':' + operation]
}

/* ===== AGENT CRUD ===== */
async function fetchAgents() {
  loading.value = true
  try {
    const { data } = await agentsApi.list()
    agents.value = data.data?.agents || []
  } catch (e) {
    console.error('Failed to load agents:', e)
  } finally {
    loading.value = false
  }
}

/** Debounced fetchAgents — coalesces rapid calls (e.g. when parallel ops complete) */
function fetchAgentsDebounced() {
  if (fetchDebounceTimer) clearTimeout(fetchDebounceTimer)
  fetchDebounceTimer = setTimeout(() => {
    fetchDebounceTimer = null
    fetchAgents()
  }, 300)
}

function openAdd() {
  editingAgent.value = null
  form.value = { owner: '', username: '', base_url: 'https://a2u4k.ee88dly.com', password: '' }
  formError.value = ''
  showModal.value = true
  nextTick(() => layui.use(['form'], (f) => f.render()))
}

function openEdit(agent) {
  editingAgent.value = agent
  form.value = { owner: agent.owner, username: agent.username, base_url: agent.base_url, password: '' }
  formError.value = ''
  showModal.value = true
  nextTick(() => layui.use(['form'], (f) => f.render()))
}

async function saveAgent() {
  formError.value = ''
  if (!form.value.owner.trim()) { formError.value = t('settings.ownerRequired'); return }
  if (!form.value.username.trim()) { formError.value = t('settings.usernameRequired2'); return }
  if (!form.value.base_url.trim()) { formError.value = t('settings.baseUrlRequired'); return }

  try {
    if (editingAgent.value) {
      const payload = { owner: form.value.owner, base_url: form.value.base_url }
      if (form.value.password) payload.password = form.value.password
      const { data } = await agentsApi.update(editingAgent.value.id, payload)
      if (data.code !== 0) { formError.value = data.message || t('settings.updateFailed'); return }
    } else {
      const payload = { owner: form.value.owner, username: form.value.username, base_url: form.value.base_url }
      if (form.value.password) payload.password = form.value.password
      const { data } = await agentsApi.create(payload)
      if (data.code !== 0) { formError.value = data.message || t('settings.createFailed'); return }
    }
    showModal.value = false
    await fetchAgents()
  } catch (e) {
    formError.value = e.response?.data?.detail || t('settings.unknownError')
  }
}

async function deleteAgent(agent) {
  layui.use(['layer'], (layer) => {
    layer.confirm(
      t('settings.deleteAgentWarning', { name: agent.owner, username: agent.username }),
      { title: t('settings.deleteAgentTitle'), btn: [t('common.confirm'), t('common.cancel')], icon: 0, area: ['420px'] },
      async (index) => {
        layer.close(index)
        try {
          await agentsApi.delete(agent.id)
          await fetchAgents()
        } catch (e) {
          layer.msg(t('settings.deleteFailed') + ': ' + (e.response?.data?.detail || e.message), { icon: 2 })
        }
      }
    )
  })
}

async function clearAgentData(agent) {
  layui.use(['layer'], (layer) => {
    layer.confirm(
      t('settings.clearDataWarning', { name: agent.owner, username: agent.username }),
      { title: t('settings.clearDataTitle'), btn: [t('common.confirm'), t('common.cancel')], icon: 0, area: ['420px'] },
      async (index) => {
        layer.close(index)
        try {
          const { data } = await agentsApi.clearData(agent.id)
          if (data.code === 0) {
            layer.msg(t('settings.clearDataSuccess', { name: agent.owner }), { icon: 1 })
            addLog('🗑 ' + agent.owner + ' > ' + t('settings.clearDataSuccess', { name: agent.owner }), 'ok')
            delete agentSync.value[agent.id]
            reloadTreeData()
          } else {
            layer.msg(data.message || t('settings.clearDataFailed'), { icon: 2 })
          }
        } catch (e) {
          layer.msg(t('settings.clearDataFailed') + ': ' + (e.response?.data?.detail || e.message), { icon: 2 })
        }
      }
    )
  })
}

/* ===== COOKIE CHECK ===== */
async function checkCookie(agent) {
  if (isAgentLocked(agent.id, 'check')) return
  lockAgent(agent.id, 'check')
  checkLoading.value[agent.id] = true
  try {
    const { data } = await agentsApi.checkCookie(agent.id)
    const result = data.data
    if (result.is_valid) {
      addLog('✓ ' + agent.owner + ' > ' + t('settings.cookieStillValid'), 'ok')
    } else {
      addLog('✗ ' + agent.owner + ' > ' + result.message, 'warn')
    }
  } catch (e) {
    addLog('✗ ' + agent.owner + ' > ' + t('settings.checkCookieError') + ': ' + e.message, 'error')
  } finally {
    checkLoading.value[agent.id] = false
    unlockAgent(agent.id, 'check')
  }
}

async function checkAllCookies() {
  const withCookie = agents.value.filter(a => a.cookie_set)
  if (withCookie.length === 0) {
    addLog('⚠ ' + t('settings.noAgentCookie'), 'warn')
    return
  }
  addLog('↻ ' + t('settings.checkingCookies') + ' ' + withCookie.length + ' ' + t('settings.agents2') + '...', 'info')
  await Promise.allSettled(withCookie.map(agent => checkCookie(agent)))
  fetchAgentsDebounced()
}

/* ===== LOGIN ===== */
async function loginAgent(agent) {
  if (isAgentLocked(agent.id, 'login')) return
  lockAgent(agent.id, 'login')
  loginLoading.value[agent.id] = true
  try {
    const { data } = await agentsApi.login(agent.id)
    if (data.code === 0) {
      addLog('✓ ' + agent.owner + ' > ' + t('settings.loginSuccess'), 'ok')
    } else {
      addLog('✗ ' + agent.owner + ' > ' + (data.message || t('settings.loginFailed')), 'error')
    }
  } catch (e) {
    addLog('✗ ' + agent.owner + ' > ' + t('common.error') + ': ' + (e.response?.data?.detail || e.message), 'error')
  } finally {
    loginLoading.value[agent.id] = false
    unlockAgent(agent.id, 'login')
  }
}

async function loginAllAgents() {
  const targets = agents.value.filter(a => a.password_set)
  if (targets.length === 0) {
    addLog('⚠ ' + t('settings.noAgentPassword'), 'warn')
    return
  }
  addLog('↻ ' + t('settings.loggingIn') + ' ' + targets.length + ' ' + t('settings.agents2') + '...', 'info')
  await Promise.allSettled(targets.map(agent => loginAgent(agent)))
  fetchAgentsDebounced()
}

/* ===== SYNC ===== */
function getWsUrl() {
  const apiUrl = import.meta.env.VITE_API_URL
  const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws'
  const httpUrl = apiUrl.replace(/^https?/, wsProtocol)
  return httpUrl + '/sync/ws?token=' + encodeURIComponent(authStore.accessToken)
}

function parseDateRange(rangeStr) {
  if (!rangeStr) return null
  const parts = rangeStr.split(' - ')
  if (parts.length !== 2) return null
  const convert = (dmy) => {
    const bits = dmy.split('/')
    return bits[2] + '-' + bits[1] + '-' + bits[0]
  }
  return convert(parts[0]) + '|' + convert(parts[1])
}

function getDataDate() {
  if (syncDate.value) return parseDateRange(syncDate.value) || syncDate.value
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  const today = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate())
  return today + '|' + today
}

function initAgentSync(agentId) {
  if (!agentSync.value[agentId]) {
    agentSync.value[agentId] = {
      status: 'idle',
      progress: { done: 0, total: 0 },
      results: {},
      totalRows: 0,
      error: '',
      lastSyncAt: null,
      detailStatus: {},
      verifyStatus: '',
      verifyResults: {},
    }
  }
  return agentSync.value[agentId]
}

function syncAgent(agent) {
  if (!agent.cookie_set) {
    addLog('⚠ ' + agent.owner + ' > ' + t('settings.noCookieNeedLogin'), 'warn')
    return
  }
  if (isAgentLocked(agent.id, 'sync')) return
  const state = initAgentSync(agent.id)
  if (state.status === 'syncing') return
  lockAgent(agent.id, 'sync')

  state.status = 'syncing'
  state.progress = { done: 0, total: 0 }
  state.results = {}
  state.totalRows = 0
  state.error = ''
  state.detailStatus = {}
  state.verifyStatus = ''
  state.verifyResults = {}
  reloadTreeData()

  const startTime = Date.now()
  addLog('↻ ' + agent.owner + ' > ' + t('settings.startSync') + ' (' + getDataDate() + ')...', 'info')

  const ws = new WebSocket(getWsUrl())
  wsMap[agent.id] = ws

  ws.onopen = () => {
    ws.send(JSON.stringify({
      base_url: agent.base_url,
      cookies: '__from_agent__',
      agent_id: agent.id,
      max_pages: 0,
      data_date: getDataDate(),
      endpoints: allEndpoints.map(e => e.key),
    }))
  }

  ws.onmessage = (event) => {
    let msg
    try { msg = JSON.parse(event.data) } catch { return }

    if (msg.type === 'start') {
      state.progress = { done: 0, total: msg.total }
    } else if (msg.type === 'detail') {
      const key = msg.endpoint
      if (msg.phase === 'fetching') {
        state.detailStatus[key] = msg.page + '/' + msg.total_pages + ' (' + msg.rows_so_far.toLocaleString() + ' ' + t('settings.rowsUnit') + ')'
      } else if (msg.phase === 'saving') {
        state.detailStatus[key] = t('settings.savingRows', { count: msg.rows.toLocaleString() })
      } else if (msg.phase === 'smart_skip') {
        const epLabel = allEndpoints.find(e => e.key === key)?.label || key
        if (msg.all_locked) {
          addLog('  🔒 ' + agent.owner + ' > ' + epLabel + ': ' + t('settings.skipAllLockedDays', { count: msg.locked_count }), 'info')
        } else {
          addLog('  🔒 ' + agent.owner + ' > ' + epLabel + ': ' + t('settings.partialLockedDays', { count: msg.locked_count }), 'info')
        }
      }
    } else if (msg.type === 'progress') {
      const key = msg.endpoint
      state.results[key] = msg.result
      state.progress.done++
      delete state.detailStatus[key]

      if (msg.result && !msg.result.error && !msg.result.skipped) {
        state.totalRows += (msg.result.fetched || 0)
      }

      const epLabel = allEndpoints.find(e => e.key === key)?.label || key
      if (msg.result?.error) {
        addLog('  ✗ ' + agent.owner + ' > ' + epLabel + ': ' + msg.result.error, 'error')
      } else if (msg.result?.skipped) {
        addLog('  ⊘ ' + agent.owner + ' > ' + epLabel + ': ' + msg.result.reason, 'warn')
      } else {
        const rows = msg.result?.fetched || 0
        addLog('  ✓ ' + agent.owner + ' > ' + epLabel + ': ' + rows.toLocaleString() + ' ' + t('settings.rowsUnit'), 'ok')
      }
    } else if (msg.type === 'verify_start') {
      state.verifyStatus = 'verifying'
      addLog('🔍 ' + agent.owner + ' > ' + t('settings.verifyingData'), 'info')
    } else if (msg.type === 'verify_detail') {
      const key = msg.endpoint
      if (msg.phase === 'verify_sampling') {
        state.detailStatus[key] = t('settings.verifyPhase', { sample: msg.sample_count, total: msg.unlocked_count })
      } else if (msg.phase === 'verify_check') {
        const icon = msg.match ? '✓' : '✗'
        state.detailStatus[key] = 'Verify ' + msg.date + ': ' + icon
      } else if (msg.phase === 'verify_locked') {
        state.detailStatus[key] = '🔒 ' + t('settings.verifyLockedDays', { count: msg.locked_count })
      } else if (msg.phase === 'verify_mismatch') {
        state.detailStatus[key] = '⚠ ' + t('settings.mismatchedDays', { count: msg.mismatch_count })
      }
    } else if (msg.type === 'verify_result') {
      const key = msg.endpoint
      state.verifyResults[key] = msg.result
      delete state.detailStatus[key]
      const epLabel = allEndpoints.find(e => e.key === key)?.label || key
      if (msg.result.status === 'locked') {
        addLog('  🔒 ' + agent.owner + ' > ' + epLabel + ': ' + t('settings.verifyLockedResult', { count: msg.result.locked_count, verified: msg.result.verified }), 'ok')
      } else if (msg.result.status === 'mismatch') {
        const mm = msg.result.mismatches || []
        const details = mm.map(m => m.date + '(DB:' + m.db + ' vs UP:' + m.upstream + ')').join(', ')
        addLog('  ⚠ ' + agent.owner + ' > ' + epLabel + ': ' + t('settings.dataMismatchDetail', { details: details }), 'warn')
      } else if (msg.result.status === 'skip') {
        addLog('  ⊘ ' + agent.owner + ' > ' + epLabel + ': ' + (msg.result.reason || t('settings.skipVerify')), 'info')
      }
    } else if (msg.type === 'verify_done') {
      state.verifyStatus = 'done'
      addLog('🔍 ' + agent.owner + ' > ' + t('settings.verifyComplete'), 'ok')
    } else if (msg.type === 'done') {
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1)
      state.status = 'done'
      state.lastSyncAt = formatDateTime(new Date())
      const results = msg.results || {}
      const errCount = Object.values(results).filter(r => r?.error).length
      addLog('✓ ' + agent.owner + ' > ' + t('settings.syncComplete') + ' ' + elapsed + t('settings.seconds') + ' — ' + errCount + ' ' + t('settings.errors'), errCount > 0 ? 'warn' : 'ok')
      delete wsMap[agent.id]
      unlockAgent(agent.id, 'sync')
      checkGlobalDone()
      fetchAgentsDebounced()
    } else if (msg.type === 'error') {
      state.status = 'error'
      state.error = msg.message || t('settings.syncFailed')
      addLog('✗ ' + agent.owner + ' > ' + state.error, 'error')
      delete wsMap[agent.id]
      unlockAgent(agent.id, 'sync')
      checkGlobalDone()
      fetchAgentsDebounced()
    }
    reloadTreeData()
  }

  ws.onerror = () => {
    state.status = 'error'
    state.error = t('settings.wsDisconnected')
    addLog('✗ ' + agent.owner + ' > ' + t('settings.wsDisconnected'), 'error')
    delete wsMap[agent.id]
    unlockAgent(agent.id, 'sync')
    checkGlobalDone()
    reloadTreeData()
  }

  ws.onclose = (event) => {
    if (state.status === 'syncing') {
      state.status = 'error'
      state.error = event.code === 4001 ? t('settings.wsTokenExpired') : t('settings.wsClosed')
      addLog('✗ ' + agent.owner + ' > ' + state.error, 'error')
    }
    delete wsMap[agent.id]
    unlockAgent(agent.id, 'sync')
    checkGlobalDone()
    reloadTreeData()
  }
}

function syncAll() {
  if (syncableAgents.value.length === 0) {
    addLog('⚠ ' + t('settings.noAgentCookieSync'), 'warn')
    return
  }
  globalSyncing.value = true
  addLog('↻ ' + t('settings.startSyncAll') + ' ' + syncableAgents.value.length + ' ' + t('settings.agents2') + ' (' + getDataDate() + ')...', 'info')
  syncableAgents.value.forEach(agent => syncAgent(agent))
}

function checkGlobalDone() {
  const anyStillSyncing = agents.value.some(a => agentSync.value[a.id]?.status === 'syncing')
  if (!anyStillSyncing) globalSyncing.value = false
}

function stopSync(agent) {
  const ws = wsMap[agent.id]
  if (ws) {
    ws.close()
    delete wsMap[agent.id]
  }
  const state = agentSync.value[agent.id]
  if (state && state.status === 'syncing') {
    state.status = 'error'
    state.error = t('settings.stopped')
    addLog('⊘ ' + agent.owner + ' > ' + t('settings.stoppedSync'), 'warn')
  }
  unlockAgent(agent.id, 'sync')
  checkGlobalDone()
  reloadTreeData()
}

function clearAllSync() {
  agentSync.value = {}
  syncLog.value = []
  reloadTreeData()
}

/* ===== HELPERS ===== */
function formatDateTime(d) {
  const pad = (n) => String(n).padStart(2, '0')
  return pad(d.getDate()) + '/' + pad(d.getMonth() + 1) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes())
}

function addLog(text, type) {
  type = type || 'info'
  const time = new Date().toLocaleTimeString(numLocale[locale.value] || 'vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  syncLog.value.push({ time: time, text: text, type: type })
  nextTick(() => {
    const el = document.querySelector('.sync-log-body')
    if (el) el.scrollTop = el.scrollHeight
  })
}

function clearLog() {
  syncLog.value = []
}

/* ===== LAYUI TIPS (event delegation cho treeTable) ===== */
function setupTableTips() {
  const container = document.querySelector('.layui-table-view[lay-id="agentTree"]')
  if (!container) return

  container._tipsEnter = (e) => {
    const btn = e.target.closest('[title]')
    if (!btn || !btn.title) return
    const content = btn.title
    btn.dataset.tipContent = content
    btn.removeAttribute('title')
    layui.use('layer', (layer) => {
      if (tipsIndex != null) layer.close(tipsIndex)
      tipsIndex = layer.tips(content, btn, {
        tips: [1, '#2e2a25'],
        time: 0,
        tipsMore: false,
      })
    })
  }

  container._tipsLeave = (e) => {
    const btn = e.target.closest('[data-tip-content]')
    if (!btn) return
    btn.setAttribute('title', btn.dataset.tipContent)
    delete btn.dataset.tipContent
    if (tipsIndex != null) {
      layui.use('layer', (layer) => {
        layer.close(tipsIndex)
        tipsIndex = null
      })
    }
  }

  container.addEventListener('mouseenter', container._tipsEnter, true)
  container.addEventListener('mouseleave', container._tipsLeave, true)
}

function cleanupTableTips() {
  const container = document.querySelector('.layui-table-view[lay-id="agentTree"]')
  if (container) {
    if (container._tipsEnter) container.removeEventListener('mouseenter', container._tipsEnter, true)
    if (container._tipsLeave) container.removeEventListener('mouseleave', container._tipsLeave, true)
  }
  if (tipsIndex != null) {
    layui.use('layer', (layer) => {
      layer.close(tipsIndex)
      tipsIndex = null
    })
  }
}

/* ===== WATCH ===== */
watch(agents, () => {
  if (treeTableReady) reloadTreeData()
})

/* ===== LIFECYCLE ===== */
onMounted(() => {
  createTemplate('tplAgentToolbar', `<div class="layui-btn-container"><button class="layui-btn layui-btn-sm layui-btn-normal" lay-event="syncAll"><i class="layui-icon layui-icon-refresh"></i> ${t('settings.syncAll')}</button><button class="layui-btn layui-btn-sm layui-btn-warm" lay-event="loginAll"><i class="layui-icon layui-icon-key"></i> ${t('settings.loginAll')}</button><button class="layui-btn layui-btn-sm layui-btn-primary" lay-event="checkAll"><i class="layui-icon layui-icon-vercode"></i> ${t('settings.checkCookie')}</button><button class="layui-btn layui-btn-sm layui-btn-primary" lay-event="addAgent"><i class="layui-icon layui-icon-add-1"></i> ${t('settings.addAgent')}</button><button class="layui-btn layui-btn-sm layui-btn-primary" lay-event="clearResults"><i class="layui-icon layui-icon-delete"></i> ${t('settings.clearResults')}</button></div>`)

  createTemplate('tplAgentRowBar', `{{# if(d._isAgent){ }}<div class="layui-btn-container">{{# var ag = JSON.parse(d._agentData); }}{{# if(ag.cookie_set){ }}<a class="layui-btn layui-btn-xs layui-btn-normal" lay-event="syncAgent" title="${t('settings.syncAgent')}"><i class="layui-icon layui-icon-refresh"></i></a>{{# } else { }}<a class="layui-btn layui-btn-xs layui-btn-disabled" title="${t('settings.needLogin')}"><i class="layui-icon layui-icon-refresh"></i></a>{{# } }}{{# if(ag.password_set){ }}<a class="layui-btn layui-btn-xs layui-btn-warm" lay-event="loginAgent" title="${t('settings.autoLogin')}"><i class="layui-icon layui-icon-key"></i></a>{{# } else { }}<a class="layui-btn layui-btn-xs layui-btn-disabled" title="${t('settings.needPassword')}"><i class="layui-icon layui-icon-key"></i></a>{{# } }}{{# if(ag.cookie_set){ }}<a class="layui-btn layui-btn-xs layui-btn-primary" lay-event="checkCookie" title="${t('settings.checkCookie')}"><i class="layui-icon layui-icon-vercode"></i></a>{{# } else { }}<a class="layui-btn layui-btn-xs layui-btn-disabled" title="${t('settings.noCookie')}"><i class="layui-icon layui-icon-vercode"></i></a>{{# } }}<a class="layui-btn layui-btn-xs layui-btn-primary" lay-event="editAgent" title="${t('common.edit')}"><i class="layui-icon layui-icon-edit"></i></a><a class="layui-btn layui-btn-xs layui-btn-danger" lay-event="clearData" title="${t('settings.clearData')}"><i class="layui-icon layui-icon-fonts-clear"></i></a><a class="layui-btn layui-btn-xs layui-btn-danger" lay-event="deleteAgent" title="${t('common.delete')}"><i class="layui-icon layui-icon-delete"></i></a></div>{{# } }}`)

  fetchAgents().then(() => {
    renderTreeTable()
  })

  nextTick(() => {
    layui.use(['form'], (form) => {
      form.render()
    })
    initDateRange('#syncDatePicker', {
      done(value) {
        syncDate.value = value
      }
    })
  })
})

onUnmounted(() => {
  cleanupTableTips()
  if (fetchDebounceTimer) clearTimeout(fetchDebounceTimer)
  Object.values(wsMap).forEach(ws => ws?.close())
  wsMap = {}
  treeTableReady = false
  const oldView = document.querySelector('.layui-table-view[lay-id="agentTree"]')
  if (oldView) oldView.remove()
})
</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-transfer"></i> {{ t('settings.agents') }}
        <span v-if="globalStatusLabel" class="tt-badge" :class="'tt-badge--' + globalStatus">
          {{ globalStatusLabel }}
        </span>
      </h3>
    </div>

    <div class="data-search-bar">
      <div class="data-search-fields">
        <div class="data-search-field">
          <label>{{ t('settings.syncTime') }}</label>
          <input id="syncDatePicker" type="text" class="layui-input" :placeholder="t('common.startEnd')" readonly />
        </div>
      </div>
    </div>

    <div v-if="loading && agents.length === 0" style="text-align:center;padding:40px;color:#999">
      <i class="layui-icon layui-icon-loading layui-anim layui-anim-rotate layui-anim-loop"></i> {{ t('common.loading') }}
    </div>

    <table class="layui-hide" id="agentTreeTable" lay-filter="agentTree"></table>

    <div v-if="syncLog.length" class="tt-log">
      <div class="tt-log-header">
        <span class="tt-log-title"><i class="layui-icon layui-icon-log"></i> {{ t('settings.log') }}</span>
        <button class="layui-btn layui-btn-xs layui-btn-primary" @click="clearLog" style="opacity: 0.7"><i class="layui-icon layui-icon-delete"></i></button>
      </div>
      <div class="sync-log-body">
        <div v-for="(entry, i) in syncLog" :key="i" class="tt-log-line" :class="'log-' + entry.type">
          <span class="log-time">[{{ entry.time }}]</span>
          <span class="log-text">{{ entry.text }}</span>
        </div>
      </div>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="showModal" class="agent-modal-overlay" @click.self="showModal = false">
      <div class="agent-modal">
        <div class="agent-modal-header">
          <h4>{{ editingAgent ? t('settings.editAgent') : t('settings.addNewAgent') }}</h4>
          <i class="layui-icon layui-icon-close agent-modal-close" @click="showModal = false"></i>
        </div>
        <div class="agent-modal-body">
          <div v-if="formError" class="agent-form-error">
            <i class="layui-icon layui-icon-close-fill"></i> {{ formError }}
          </div>
          <div class="agent-form-field">
            <label>{{ t('settings.agentOwner') }}</label>
            <input v-model="form.owner" type="text" class="layui-input" :placeholder="t('settings.agentOwnerPlaceholder')" />
          </div>
          <div class="agent-form-field">
            <label>{{ t('settings.agentUsername') }}</label>
            <input v-model="form.username" type="text" class="layui-input" :placeholder="t('settings.agentUsernamePlaceholder')" :disabled="!!editingAgent" />
          </div>
          <div class="agent-form-field">
            <label>{{ t('settings.agentBaseUrl') }}</label>
            <input v-model="form.base_url" type="text" class="layui-input" :placeholder="t('settings.agentBaseUrlPlaceholder')" />
          </div>
          <div class="agent-form-field">
            <label>{{ editingAgent ? t('settings.agentPasswordKeep') : t('settings.agentPassword') }}</label>
            <input v-model="form.password" type="password" class="layui-input" :placeholder="t('settings.agentPasswordPlaceholder')" />
          </div>
        </div>
        <div class="agent-modal-footer">
          <button class="layui-btn layui-btn-sm layui-btn-primary" @click="showModal = false">{{ t('common.cancel') }}</button>
          <button class="layui-btn layui-btn-sm layui-btn-normal" @click="saveAgent">
            <i class="layui-icon layui-icon-ok"></i> {{ editingAgent ? t('settings.updateBtn') : t('settings.createNew') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.tt-badge { font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 10px; margin-left: 10px; vertical-align: middle; }
.tt-badge--syncing { color: #16baaa; background: rgba(22,186,170,0.08); }
.tt-badge--done { color: #27ae60; background: rgba(39,174,96,0.08); }
.tt-badge--error { color: #e74c3c; background: rgba(231,76,60,0.08); }

.tt-log { margin-top: 12px; border: 1px solid #e6e2da; border-radius: 4px; overflow: hidden; }
.tt-log-header { display: flex; align-items: center; justify-content: space-between; padding: 5px 12px; background: #2e2a25; }
.tt-log-title { font-size: 12px; font-weight: 600; color: #aaa; display: flex; align-items: center; gap: 5px; }
.tt-log-title .layui-icon { font-size: 14px; }
.sync-log-body { background: #1e1c19; padding: 8px 12px; max-height: 220px; overflow-y: auto; font-family: 'SF Mono', Consolas, Monaco, monospace; font-size: 11.5px; line-height: 1.7; }
.tt-log-line { display: flex; gap: 8px; white-space: pre-wrap; word-break: break-all; }
.log-time { color: #666; flex-shrink: 0; }
.log-info .log-text { color: #ddd; }
.log-ok .log-text { color: #5fb878; }
.log-warn .log-text { color: #ffb800; font-weight: 600; }
.log-error .log-text { color: #ff5722; font-weight: 600; }
</style>

<style>
.tt-cookie { display: inline-block; font-size: 11px; font-weight: 600; padding: 1px 6px; border-radius: 3px; }
.tt-cookie--none { color: #999; background: rgba(0,0,0,0.04); }
.tt-cookie--unknown { color: #f57f17; background: rgba(245,127,23,0.06); }
.tt-cookie--valid { color: #27ae60; background: rgba(39,174,96,0.06); }
.tt-cookie--expired { color: #e74c3c; background: rgba(231,76,60,0.06); }

.tt-status { display: inline-block; font-size: 11px; font-weight: 600; padding: 1px 6px; border-radius: 3px; white-space: nowrap; }
.tt-status--idle { color: #aaa; }
.tt-status--syncing { color: #16baaa; background: rgba(22,186,170,0.06); }
.tt-status--done { color: #27ae60; background: rgba(39,174,96,0.06); }
.tt-status--error { color: #e74c3c; background: rgba(231,76,60,0.06); }
.tt-status--skip { color: #f57f17; background: rgba(245,127,23,0.06); }

.tt-sub { color: #999; font-weight: 400; font-size: 11px; margin-left: 4px; }

.tt-bar { position: relative; height: 16px; background: #f0ede6; border-radius: 2px; overflow: hidden; min-width: 80px; }
.tt-bar-fill { position: absolute; top: 0; left: 0; height: 100%; border-radius: 2px; transition: width 0.3s ease; }
.tt-fill--syncing { background: #16baaa; }
.tt-fill--done { background: #5fb878; }
.tt-fill--error { background: #e74c3c; }
.tt-bar-text { position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: flex-end; padding: 0 6px; font-size: 10.5px; font-weight: 600; color: #555; }

.tt-note { font-size: 11px; color: #888; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: inline-block; }
.tt-err { color: #e74c3c; font-size: 11px; font-weight: 600; }
.tt-lock { font-size: 12px; cursor: help; }
.tt-lock-warn { font-size: 12px; cursor: help; color: #f57f17; }

.layui-btn-disabled { background-color: #d2d2d2 !important; border-color: #d2d2d2 !important; color: #fff !important; cursor: not-allowed !important; pointer-events: none; }

.agent-modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.35); z-index: 19999; display: flex; align-items: center; justify-content: center; }
.agent-modal { background: #fff; border-radius: 6px; width: 380px; max-width: 92vw; box-shadow: 0 6px 24px rgba(0,0,0,0.18); }
.agent-modal-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid #e6e2da; }
.agent-modal-header h4 { margin: 0; font-size: 14px; font-weight: 700; color: #2e2a25; }
.agent-modal-close { font-size: 16px; color: #999; cursor: pointer; transition: color 0.15s; }
.agent-modal-close:hover { color: #e74c3c; }
.agent-modal-body { padding: 14px 16px; display: flex; flex-direction: column; gap: 12px; }
.agent-form-error { display: flex; align-items: center; gap: 6px; background: rgba(231,76,60,0.06); border: 1px solid rgba(231,76,60,0.15); border-radius: 4px; color: #c0392b; padding: 7px 10px; font-size: 12px; }
.agent-form-error .layui-icon { font-size: 13px; }
.agent-form-field { display: flex; flex-direction: column; gap: 4px; }
.agent-form-field label { font-size: 12px; color: #666; font-weight: 600; }
.agent-form-field .layui-input { height: 32px; font-size: 13px; border-color: #e6e2da; }
.agent-form-field .layui-input:focus { border-color: #16baaa; }
.agent-form-field .layui-input:disabled { background: #f5f5f5; color: #999; }
.agent-modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 10px 16px; border-top: 1px solid #e6e2da; }
</style>
