<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()

onMounted(() => {
  createTemplate('betThirdPartyToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="${t('common.refresh')}"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      renderTable(table, {
        elem: '#betThirdPartyTable',
        id: 'betThirdPartyTable',
        cols: [[
          { field: '_agent_name', title: t('common.staff'), width: 110 },
          { field: 'serial_no', title: t('betsThirdParty.transId') },
          { field: 'platform_id_name', title: t('betsThirdParty.provider') },
          { field: 'platform_username', title: t('betsThirdParty.accountName') },
          { field: 'c_name', title: t('betsThirdParty.gameType') },
          { field: 'game_name', title: t('betsThirdParty.gameName') },
          { field: 'bet_amount', title: t('betsThirdParty.betAmount') },
          { field: 'turnover', title: t('betsThirdParty.validBet') },
          { field: 'prize', title: t('betsThirdParty.bonus') },
          { field: 'win_lose', title: t('betsThirdParty.winLoss') },
          { field: 'bet_time', title: t('betsThirdParty.betTime') },
        ]],
        url: '/api/v1/proxy/bet-orders',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        parseData(res) {
          return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
        },
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#betThirdPartyToolbar',
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

      form.on('submit(searchBetThirdParty)', (formData) => {
        var where = formData.field || {}
        var dateRange = where.date_range || ''
        delete where.date_range
        delete where.quick_date
        if (dateRange) {
          where.bet_time = dateRange
        }
        table.reload('betThirdPartyTable', { where: where })
        return false
      })

      table.on('toolbar(betThirdPartyTable)', (obj) => {
        if (obj.event === 'refresh') {
          table.reload('betThirdPartyTable')
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
        <i class="layui-icon layui-icon-game"></i> {{ t('betsThirdParty.title') }}
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="betThirdPartySearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>{{ t('deposits.accountName') }}</label>
            <input name="username" type="text" class="layui-input" :placeholder="t('betsThirdParty.enterAccountName')" />
          </div>
          <div class="data-search-field">
            <label>{{ t('betsThirdParty.transId') }}</label>
            <input name="serial_no" type="text" class="layui-input" :placeholder="t('betsThirdParty.enterTransId')" />
          </div>
          <div class="data-search-field">
            <label>{{ t('betsThirdParty.accountName') }}</label>
            <input name="platform_username" type="text" class="layui-input" :placeholder="t('betsThirdParty.enterPlatformAccount')" />
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
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchBetThirdParty">
            <i class="layui-icon layui-icon-search"></i> {{ t('common.search') }}
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> {{ t('common.reset') }}
          </button>
        </div>
      </form>
    </div>

    <table id="betThirdPartyTable" lay-filter="betThirdPartyTable"></table>
  </div>
</template>
