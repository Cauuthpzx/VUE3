<script setup>
import { onMounted, onUnmounted, nextTick, ref, watch } from 'vue'
import { agentsApi } from '@/api/agents'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'
import { useI18n } from '@/composables/useI18n'
import { useAgentSync } from '@/composables/useAgentSync'
import { escapeHtml, NUM_LOCALE } from '@/utils/constants'
import AgentFormModal from './AgentFormModal.vue'
import SyncLogPanel from './SyncLogPanel.vue'

const { t, locale } = useI18n()
const numLocale = NUM_LOCALE
const { createTemplate } = useLayuiTemplate()

/* ===== STATE ===== */
const agents = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingAgent = ref(null)
const syncLog = ref([])

let treeTableReady = false
let fetchDebounceTimer = null

function addLog(text, type) {
  type = type || 'info'
  const time = new Date().toLocaleTimeString(numLocale[locale.value] || 'vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  syncLog.value.push({ time, text, type })
}

function clearLog() {
  syncLog.value = []
}

/* ===== SYNC COMPOSABLE ===== */
const {
  agentSync, globalStatus, globalStatusLabel, syncDate,
  allEndpoints, syncAgent, syncAll, stopSync, clearAllSync,
  loginAgent, loginAllAgents, checkCookie, checkAllCookies,
  closeAllWs,
} = useAgentSync(agents, addLog, fetchAgentsDebounced)

/* ===== AGENT CRUD ===== */
async function fetchAgents() {
  loading.value = true
  try {
    const { data } = await agentsApi.list()
    agents.value = data.data?.agents || []
  } catch {
    // Silently fail — UI shows empty state
  } finally {
    loading.value = false
  }
}

function fetchAgentsDebounced() {
  if (fetchDebounceTimer) clearTimeout(fetchDebounceTimer)
  fetchDebounceTimer = setTimeout(() => {
    fetchDebounceTimer = null
    fetchAgents()
  }, 300)
}

function openAdd() {
  editingAgent.value = null
  showModal.value = true
}

function openEdit(agent) {
  editingAgent.value = agent
  showModal.value = true
}

async function deleteAgent(agent) {
  layui.use(['layer'], (layer) => {
    layer.confirm(
      t('settings.deleteAgentWarning', { name: escapeHtml(agent.owner), username: escapeHtml(agent.username) }),
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
      t('settings.clearDataWarning', { name: escapeHtml(agent.owner), username: escapeHtml(agent.username) }),
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
        progress: epNote ? '<span class="tt-note" title="' + escapeHtml(epNote) + '">' + escapeHtml(epNote) + '</span>' : '',
        rows: epRows,
        saved: epSaved,
        time: '',
      }
    })

    return {
      id: agent.id,
      _isAgent: true,
      _agentData: JSON.stringify({
        id: agent.id, owner: agent.owner, username: agent.username,
        base_url: agent.base_url, cookie_set: agent.cookie_set,
        password_set: agent.password_set, cookie_status: cookieStatus,
      }),
      _syncStatus: status,
      name: '<strong>' + escapeHtml(agent.owner) + '</strong> <span class="tt-sub">' + escapeHtml(agent.username) + '</span>',
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
        tree: { customName: { children: 'children' }, view: { showIcon: false } },
        toolbar: '#tplAgentToolbar',
        defaultToolbar: [
          { title: t('table.filter'), layEvent: 'LAYTABLE_COLS', icon: 'layui-icon-cols' },
          { title: t('table.exports'), layEvent: 'LAYTABLE_EXPORT', icon: 'layui-icon-export' },
          { title: t('table.print'), layEvent: 'LAYTABLE_PRINT', icon: 'layui-icon-print' },
        ],
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
        skin: 'grid', even: true, size: 'sm', page: false,
        text: { none: t('settings.noAgentYet') },
      })

      treeTableReady = true

      treeTable.on('toolbar(agentTree)', (obj) => {
        switch (obj.event) {
          case 'syncAll': syncAll(reloadTreeData); break
          case 'loginAll': loginAllAgents(); break
          case 'checkAll': checkAllCookies(); break
          case 'addAgent': openAdd(); break
          case 'clearResults': clearAllSync(reloadTreeData); syncLog.value = []; break
        }
      })

      treeTable.on('tool(agentTree)', (obj) => {
        if (!obj.data._isAgent) return
        let agent
        try { agent = JSON.parse(obj.data._agentData) } catch { return }

        switch (obj.event) {
          case 'syncAgent': syncAgent(agent, reloadTreeData); break
          case 'stopSync': stopSync(agent, reloadTreeData); break
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

/* ===== WATCH ===== */
watch(agents, () => {
  if (treeTableReady) reloadTreeData()
})

/* ===== LIFECYCLE ===== */
onMounted(() => {
  createTemplate('tplAgentToolbar', `<div class="layui-btn-container"><button class="layui-btn layui-btn-sm layui-btn-normal" lay-event="syncAll"><i class="layui-icon layui-icon-refresh"></i> ${t('settings.syncAll')}</button><button class="layui-btn layui-btn-sm layui-btn-warm" lay-event="loginAll"><i class="layui-icon layui-icon-key"></i> ${t('settings.loginAll')}</button><button class="layui-btn layui-btn-sm layui-btn-primary" lay-event="checkAll"><i class="layui-icon layui-icon-vercode"></i> ${t('settings.checkCookie')}</button><button class="layui-btn layui-btn-sm layui-btn-primary" lay-event="addAgent"><i class="layui-icon layui-icon-add-1"></i> ${t('settings.addAgent')}</button><button class="layui-btn layui-btn-sm layui-btn-primary" lay-event="clearResults"><i class="layui-icon layui-icon-delete"></i> ${t('settings.clearResults')}</button></div>`)

  createTemplate('tplAgentRowBar', `{{# if(d._isAgent){ }}<div class="layui-btn-container">{{# var ag = JSON.parse(d._agentData); }}{{# if(ag.cookie_set){ }}<a class="layui-btn layui-btn-xs layui-btn-normal" lay-event="syncAgent" title="${t('settings.syncAgent')}"><i class="layui-icon layui-icon-refresh"></i></a>{{# } else { }}<a class="layui-btn layui-btn-xs layui-btn-disabled" title="${t('settings.needLogin')}"><i class="layui-icon layui-icon-refresh"></i></a>{{# } }}{{# if(ag.password_set){ }}<a class="layui-btn layui-btn-xs layui-btn-warm" lay-event="loginAgent" title="${t('settings.autoLogin')}"><i class="layui-icon layui-icon-key"></i></a>{{# } else { }}<a class="layui-btn layui-btn-xs layui-btn-disabled" title="${t('settings.needPassword')}"><i class="layui-icon layui-icon-key"></i></a>{{# } }}{{# if(ag.cookie_set){ }}<a class="layui-btn layui-btn-xs layui-btn-primary" lay-event="checkCookie" title="${t('settings.checkCookie')}"><i class="layui-icon layui-icon-vercode"></i></a>{{# } else { }}<a class="layui-btn layui-btn-xs layui-btn-disabled" title="${t('settings.noCookie')}"><i class="layui-icon layui-icon-vercode"></i></a>{{# } }}<a class="layui-btn layui-btn-xs layui-btn-primary" lay-event="editAgent" title="${t('common.edit')}"><i class="layui-icon layui-icon-edit"></i></a><a class="layui-btn layui-btn-xs layui-btn-danger" lay-event="clearData" title="${t('settings.clearData')}"><i class="layui-icon layui-icon-fonts-clear"></i></a><a class="layui-btn layui-btn-xs layui-btn-danger" lay-event="deleteAgent" title="${t('common.delete')}"><i class="layui-icon layui-icon-delete"></i></a></div>{{# } }}`)

  fetchAgents().then(() => renderTreeTable())

  nextTick(() => {
    layui.use(['form'], (form) => {
      form.render()
      form.on('select(quickDateAgent)', (data) => {
        var input = document.getElementById('syncDatePicker')
        if (input) {
          var val = quickDateValue(data.value)
          input.value = val
          syncDate.value = val
        }
      })
    })
    initDateRange('#syncDatePicker', {
      done(value) { syncDate.value = value }
    })
  })
})

onUnmounted(() => {
  if (fetchDebounceTimer) clearTimeout(fetchDebounceTimer)
  closeAllWs()
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
      <form class="layui-form" lay-filter="agentSyncForm">
        <div class="data-search-fields">
          <div class="data-search-field" style="min-width:auto;width:150px">
            <label>{{ t('common.quickSelect') }}</label>
            <select name="quick_date" lay-filter="quickDateAgent">
              <option value="">{{ t('common.selectQuick') }}</option>
              <option value="today">{{ t('common.today') }}</option>
              <option value="yesterday">{{ t('common.yesterday') }}</option>
              <option value="7days">{{ t('common.last7days') }}</option>
              <option value="thisMonth">{{ t('common.thisMonth') }}</option>
              <option value="lastMonth">{{ t('common.lastMonth') }}</option>
            </select>
          </div>
          <div class="data-search-field" style="min-width:auto;width:220px">
            <label>{{ t('settings.syncTime') }}</label>
            <input id="syncDatePicker" type="text" class="layui-input" :placeholder="t('common.startEnd')" readonly />
          </div>
        </div>
      </form>
    </div>

    <div v-if="loading && agents.length === 0" style="text-align:center;padding:40px;color:#999">
      <i class="layui-icon layui-icon-loading layui-anim layui-anim-rotate layui-anim-loop"></i> {{ t('common.loading') }}
    </div>

    <table class="layui-hide" id="agentTreeTable" lay-filter="agentTree"></table>

    <SyncLogPanel :logs="syncLog" @clear="clearLog" />
  </div>

  <AgentFormModal
    v-model:visible="showModal"
    :agent="editingAgent"
    @saved="fetchAgents"
  />
</template>

<style scoped>
.tt-badge { font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 10px; margin-left: 10px; vertical-align: middle; }
.tt-badge--syncing { color: #16baaa; background: rgba(22,186,170,0.08); }
.tt-badge--done { color: #27ae60; background: rgba(39,174,96,0.08); }
.tt-badge--error { color: #e74c3c; background: rgba(231,76,60,0.08); }
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
</style>
