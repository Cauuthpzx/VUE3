<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
const { createTemplate } = useLayuiTemplate()
const { renderTable, reloadTable, onLocaleChange } = useLayuiTable()

function initTemplates() {
  createTemplate('betsToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="${t('common.refresh')}"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)
}

function getCols() {
  return [[
    { field: '_agent_name', title: t('common.staff'), width: 110 },
    { field: 'serial_no', title: t('bets.transId') },
    { field: 'username', title: t('bets.username') },
    { field: 'create_time', title: t('bets.betTime') },
    { field: 'lottery_name', title: t('bets.game') },
    { field: 'play_type_name', title: t('bets.gameType') },
    { field: 'play_name', title: t('bets.playType') },
    { field: 'issue', title: t('bets.period') },
    { field: 'content', title: t('bets.betInfo') },
    { field: 'money', title: t('bets.betAmount') },
    { field: 'rebate_amount', title: t('bets.rebateAmount') },
    { field: 'result', title: t('bets.winLoss') },
    { field: 'status_text', title: t('common.status') },
  ]]
}

function initTable(table) {
  initTemplates()
  renderTable(table, {
    elem: '#betsTable',
    id: 'betsTable',
    cols: getCols(),
    url: '/api/v1/proxy/bets',
    method: 'post',
    contentType: 'application/x-www-form-urlencoded',
    parseData(res) {
      return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
    },
    page: { limit: 10, limits: [10, 50, 100, 200] },
    toolbar: '#betsToolbar',
    defaultToolbar: ['filter', 'exports', 'print'],
    skin: 'grid',
    even: true,
    size: 'sm',
    text: { none: t('common.noData') },
  })
}

onMounted(() => {
  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      initTable(table)

      form.render()
      initDateRange('input[name="date_range"]')

      form.on('select(quickDate)', (data) => {
        var input = document.querySelector('input[name="date_range"]')
        if (input) input.value = quickDateValue(data.value)
      })

      form.on('submit(searchBets)', (data) => {
        var whereParams = {
          username: data.field.username,
          serial_no: data.field.serial_no,
          lottery_id: data.field.lottery_id,
          status: data.field.status,
        }
        if (data.field.date_range) {
          whereParams.create_time = data.field.date_range
        }
        delete whereParams.quick_date
        table.reload('betsTable', { where: whereParams })
        return false
      })

      table.on('toolbar(betsTable)', (obj) => {
        if (obj.event === 'refresh') {
          table.reload('betsTable')
        }
      })
    })
  })
})

onLocaleChange(() => {
  initTemplates()
  layui.use(['table'], (table) => {
    reloadTable(table, 'betsTable', {
      cols: getCols(),
      toolbar: '#betsToolbar',
      defaultToolbar: ['filter', 'exports', 'print'],
      text: { none: t('common.noData') },
    })
  })
})

</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-game"></i> {{ t('bets.title') }}
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="betsSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>{{ t('bets.username') }}</label>
            <input name="username" type="text" class="layui-input" :placeholder="t('bets.enterUsername')" />
          </div>
          <div class="data-search-field">
            <label>{{ t('bets.transId') }}</label>
            <input name="serial_no" type="text" class="layui-input" :placeholder="t('bets.enterTransId')" />
          </div>
          <div class="data-search-field">
            <label>{{ t('bets.game') }}</label>
            <select name="lottery_id">
              <option value="">{{ t('common.all') }}</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>{{ t('common.status') }}</label>
            <select name="status">
              <option value="">{{ t('common.all') }}</option>
              <option value="-9">{{ t('bets.statusUnpaid') }}</option>
              <option value="1">{{ t('bets.statusWin') }}</option>
              <option value="-1">{{ t('bets.statusLose') }}</option>
              <option value="2">{{ t('bets.statusDraw') }}</option>
              <option value="3">{{ t('bets.statusCancelUser') }}</option>
              <option value="4">{{ t('bets.statusCancelSystem') }}</option>
              <option value="5">{{ t('bets.statusAbnormal') }}</option>
              <option value="6">{{ t('bets.statusUnpaidManual') }}</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>{{ t('common.quickSelect') }}</label>
            <select name="quick_date" lay-filter="quickDate">
              <option value="">{{ t('common.selectQuick') }}</option>
              <option value="today">{{ t('common.today') }}</option>
              <option value="yesterday">{{ t('common.yesterday') }}</option>
              <option value="7days">{{ t('common.last7days') }}</option>
              <option value="thisMonth">{{ t('common.thisMonth') }}</option>
              <option value="lastMonth">{{ t('common.lastMonth') }}</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>{{ t('common.selectTime') }}</label>
            <input name="date_range" type="text" class="layui-input" :placeholder="t('common.startEnd')" readonly />
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchBets">
            <i class="layui-icon layui-icon-search"></i> {{ t('common.search') }}
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> {{ t('common.reset') }}
          </button>
        </div>
      </form>
    </div>

    <table id="betsTable" lay-filter="betsTable"></table>
  </div>
</template>
