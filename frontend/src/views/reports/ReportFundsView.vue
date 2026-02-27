<script setup>
import { onMounted, nextTick, ref } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'
import { useI18n } from '@/composables/useI18n'
import { formatNumber as _formatNumber } from '@/utils/constants'

const { t, locale } = useI18n()
const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()
const totalData = ref({})

function formatNumber(val) {
  return _formatNumber(val, locale.value)
}

onMounted(() => {
  createTemplate('reportFundsToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="${t('common.refresh')}"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      renderTable(table, {
        elem: '#reportFundsTable',
        id: 'reportFundsTable',
        cols: [[
          { field: '_agent_name', title: t('common.staff'), width: 110 },
          { field: 'username', title: t('reportFunds.accountName') },
          { field: 'user_parent_format', title: t('reportFunds.belongAgent') },
          { field: 'deposit_count', title: t('reportFunds.depositCount') },
          { field: 'deposit_amount', title: t('reportFunds.depositAmountShort'), sort: true },
          { field: 'withdrawal_count', title: t('reportFunds.withdrawCount') },
          { field: 'withdrawal_amount', title: t('reportFunds.withdrawAmountShort') },
          { field: 'charge_fee', title: t('reportFunds.chargeFee') },
          { field: 'agent_commission', title: t('reportFunds.agentCommission') },
          { field: 'promotion', title: t('reportFunds.promotion') },
          { field: 'third_rebate', title: t('reportFunds.thirdRebate') },
          { field: 'third_activity_amount', title: t('reportFunds.thirdActivityAmount') },
          { field: 'date', title: t('reportFunds.time') },
        ]],
        url: '/api/v1/proxy/report-funds',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        parseData(res) {
          if (res._totals) totalData.value = res._totals
          return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
        },
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#reportFundsToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: t('common.noData') },
      })

      form.render()
      initDateRange('input[name="date_range"]')

      form.on('select(quickDate)', (data) => {
        var input = document.querySelector('input[name="date_range"]')
        if (input) input.value = quickDateValue(data.value)
      })

      form.on('submit(searchReportFunds)', (data) => {
        var params = Object.assign({}, data.field)
        delete params.quick_date
        if (params.date_range) {
          params.date = params.date_range
          delete params.date_range
        }
        table.reload('reportFundsTable', { where: params })
        return false
      })

      table.on('toolbar(reportFundsTable)', (obj) => {
        if (obj.event === 'refresh') {
          table.reload('reportFundsTable')
        }
      })
    })
  })
})

</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-chart"></i> {{ t('reportFunds.title') }}
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="reportFundsSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>{{ t('reportFunds.accountName') }}</label>
            <input name="username" type="text" class="layui-input" :placeholder="t('common.enterAccountName')" />
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
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchReportFunds">
            <i class="layui-icon layui-icon-search"></i> {{ t('common.search') }}
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> {{ t('common.reset') }}
          </button>
        </div>
      </form>
    </div>

    <table id="reportFundsTable" lay-filter="reportFundsTable"></table>

    <div v-if="totalData && Object.keys(totalData).length" class="data-total-bar">
      <h4 class="data-total-title">{{ t('reportLottery.summary') }}</h4>
      <div class="data-total-fields">
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportFunds.depositCount') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.deposit_count) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportFunds.depositAmountShort') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.deposit_amount) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportFunds.withdrawCount') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.withdrawal_count) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportFunds.withdrawAmountShort') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.withdrawal_amount) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportFunds.chargeFee') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.charge_fee) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportFunds.agentCommission') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.agent_commission) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportFunds.promotion') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.promotion) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportFunds.thirdRebate') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.third_rebate) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportFunds.thirdBonusShort') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.third_activity_amount) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
