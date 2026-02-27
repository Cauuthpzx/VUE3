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
  createTemplate('reportProviderToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="${t('common.refresh')}"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      renderTable(table, {
        elem: '#reportProviderTable',
        id: 'reportProviderTable',
        cols: [[
          { field: '_agent_name', title: t('common.staff'), width: 110 },
          { field: 'username', title: t('reportProvider.accountName') },
          { field: 'platform_id_name', title: t('reportProvider.providerGame') },
          { field: 't_bet_times', title: t('reportProvider.betCount') },
          { field: 't_bet_amount', title: t('reportProvider.betAmount') },
          { field: 't_turnover', title: t('reportProvider.validBetFull') },
          { field: 't_prize', title: t('reportProvider.bonus') },
          { field: 't_win_lose', title: t('reportProvider.winLoss') },
        ]],
        url: '/api/v1/proxy/report-third',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        parseData(res) {
          if (res._totals) totalData.value = res._totals
          return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
        },
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#reportProviderToolbar',
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

      form.on('submit(searchReportProvider)', (data) => {
        var params = Object.assign({}, data.field)
        delete params.quick_date
        if (params.date_range) {
          params.date = params.date_range
          delete params.date_range
        }
        table.reload('reportProviderTable', { where: params })
        return false
      })

      table.on('toolbar(reportProviderTable)', (obj) => {
        if (obj.event === 'refresh') {
          table.reload('reportProviderTable')
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
        <i class="layui-icon layui-icon-chart"></i> {{ t('reportProvider.providerTitle') }}
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="reportProviderSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>{{ t('reportProvider.accountName') }}</label>
            <input name="username" type="text" class="layui-input" :placeholder="t('common.enterAccountName')" />
          </div>
          <div class="data-search-field">
            <label>{{ t('reportProvider.providerGame') }}</label>
            <select name="platform_id">
              <option value="">{{ t('common.all') }}</option>
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
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchReportProvider">
            <i class="layui-icon layui-icon-search"></i> {{ t('common.search') }}
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> {{ t('common.reset') }}
          </button>
        </div>
      </form>
    </div>

    <table id="reportProviderTable" lay-filter="reportProviderTable"></table>

    <div v-if="totalData && Object.keys(totalData).length" class="data-total-bar">
      <h4 class="data-total-title">{{ t('reportLottery.summary') }}</h4>
      <div class="data-total-fields">
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportProvider.betCount') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.t_bet_times) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportProvider.betAmount') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.t_bet_amount) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportProvider.validBetFull') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.t_turnover) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportProvider.bonus') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.t_prize) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportProvider.winLoss') }}</span>
          <span class="data-total-value" :class="{ 'text-red': parseFloat(totalData.t_win_lose) < 0, 'text-green': parseFloat(totalData.t_win_lose) > 0 }">{{ formatNumber(totalData.t_win_lose) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">{{ t('reportProvider.bettors') }}</span>
          <span class="data-total-value">{{ formatNumber(totalData.username) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
