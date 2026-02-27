import { ref, computed, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'
import { NUM_LOCALE } from '@/utils/constants'
import { agentsApi } from '@/api/agents'

/**
 * Composable quản lý sync state, WebSocket, login, cookie check.
 * Tự động abort pending API calls khi component unmount.
 */
export function useAgentSync(agents, addLog, fetchAgentsDebounced) {
  const { t, locale } = useI18n()
  const numLocale = NUM_LOCALE
  const authStore = useAuthStore()

  // AbortController management — cancel pending requests on unmount
  const activeControllers = new Set()

  function createSignal() {
    const controller = new AbortController()
    activeControllers.add(controller)
    controller.signal.addEventListener('abort', () => activeControllers.delete(controller), { once: true })
    return controller.signal
  }

  function abortAll() {
    activeControllers.forEach(c => c.abort())
    activeControllers.clear()
  }

  onUnmounted(() => abortAll())

  /* ===== STATE ===== */
  const agentSync = ref({})
  const globalSyncing = ref(false)
  const syncDate = ref('')
  const loginLoading = ref({})
  const checkLoading = ref({})
  const agentLocks = ref({})

  let wsMap = {}

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

  /* ===== HELPERS: LOCK ===== */
  function isAgentLocked(agentId, operation) {
    return !!agentLocks.value[agentId + ':' + operation]
  }

  function lockAgent(agentId, operation) {
    agentLocks.value[agentId + ':' + operation] = true
  }

  function unlockAgent(agentId, operation) {
    delete agentLocks.value[agentId + ':' + operation]
  }

  /* ===== DATE HELPERS ===== */
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

  function formatDateTime(d) {
    const pad = (n) => String(n).padStart(2, '0')
    return pad(d.getDate()) + '/' + pad(d.getMonth() + 1) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes())
  }

  /* ===== COOKIE CHECK ===== */
  async function checkCookie(agent) {
    if (isAgentLocked(agent.id, 'check')) return
    lockAgent(agent.id, 'check')
    checkLoading.value[agent.id] = true
    try {
      const { data } = await agentsApi.checkCookie(agent.id, createSignal())
      const result = data.data
      if (result.is_valid) {
        addLog('✓ ' + agent.owner + ' > ' + t('settings.cookieStillValid'), 'ok')
      } else {
        addLog('✗ ' + agent.owner + ' > ' + result.message, 'warn')
      }
    } catch (e) {
      if (e.name === 'CanceledError' || e.name === 'AbortError') return
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
      const { data } = await agentsApi.login(agent.id, createSignal())
      if (data.code === 0) {
        addLog('✓ ' + agent.owner + ' > ' + t('settings.loginSuccess'), 'ok')
      } else {
        addLog('✗ ' + agent.owner + ' > ' + (data.message || t('settings.loginFailed')), 'error')
      }
    } catch (e) {
      if (e.name === 'CanceledError' || e.name === 'AbortError') return
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
    return httpUrl + '/sync/ws'
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

  function syncAgent(agent, onTreeReload) {
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
    onTreeReload()

    const startTime = Date.now()
    addLog('↻ ' + agent.owner + ' > ' + t('settings.startSync') + ' (' + getDataDate() + ')...', 'info')

    const ws = new WebSocket(getWsUrl())
    wsMap[agent.id] = ws

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'auth', token: authStore.accessToken }))
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
      handleWsMessage(msg, state, agent, startTime, onTreeReload)
    }

    ws.onerror = () => {
      state.status = 'error'
      state.error = t('settings.wsDisconnected')
      addLog('✗ ' + agent.owner + ' > ' + t('settings.wsDisconnected'), 'error')
      delete wsMap[agent.id]
      unlockAgent(agent.id, 'sync')
      checkGlobalDone()
      onTreeReload()
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
      onTreeReload()
    }
  }

  function handleWsMessage(msg, state, agent, startTime, onTreeReload) {
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
      handleProgressMessage(msg, state, agent)
    } else if (msg.type === 'verify_start') {
      state.verifyStatus = 'verifying'
      addLog('🔍 ' + agent.owner + ' > ' + t('settings.verifyingData'), 'info')
    } else if (msg.type === 'verify_detail') {
      handleVerifyDetail(msg, state)
    } else if (msg.type === 'verify_result') {
      handleVerifyResult(msg, state, agent)
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
    onTreeReload()
  }

  function handleProgressMessage(msg, state, agent) {
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
  }

  function handleVerifyDetail(msg, state) {
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
  }

  function handleVerifyResult(msg, state, agent) {
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
  }

  function syncAll(onTreeReload) {
    if (syncableAgents.value.length === 0) {
      addLog('⚠ ' + t('settings.noAgentCookieSync'), 'warn')
      return
    }
    globalSyncing.value = true
    addLog('↻ ' + t('settings.startSyncAll') + ' ' + syncableAgents.value.length + ' ' + t('settings.agents2') + ' (' + getDataDate() + ')...', 'info')
    syncableAgents.value.forEach(agent => syncAgent(agent, onTreeReload))
  }

  function checkGlobalDone() {
    const anyStillSyncing = agents.value.some(a => agentSync.value[a.id]?.status === 'syncing')
    if (!anyStillSyncing) globalSyncing.value = false
  }

  function stopSync(agent, onTreeReload) {
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
    onTreeReload()
  }

  function clearAllSync(onTreeReload) {
    agentSync.value = {}
    onTreeReload()
  }

  function closeAllWs() {
    abortAll()
    Object.values(wsMap).forEach(ws => ws?.close())
    wsMap = {}
  }

  return {
    agentSync,
    globalSyncing,
    syncDate,
    loginLoading,
    checkLoading,
    agentLocks,
    allEndpoints,
    globalStatus,
    globalStatusLabel,
    syncableAgents,
    checkCookie,
    checkAllCookies,
    loginAgent,
    loginAllAgents,
    syncAgent,
    syncAll,
    stopSync,
    clearAllSync,
    closeAllWs,
    getDataDate,
    initAgentSync,
  }
}
