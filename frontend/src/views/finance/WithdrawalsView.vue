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
  createTemplate('withdrawalsToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="${t('common.refresh')}"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      renderTable(table, {
        elem: '#withdrawalsTable',
        id: 'withdrawalsTable',
        cols: [[
          { field: '_agent_name', title: t('common.staff'), width: 110 },
          { field: 'serial_no', title: t('withdrawals.transId') },
          { field: 'create_time', title: t('withdrawals.createTime') },
          { field: 'username', title: t('withdrawals.accountName') },
          { field: 'user_parent_format', title: t('withdrawals.belongAgent') },
          { field: 'amount', title: t('withdrawals.amount') },
          { field: 'user_fee', title: t('withdrawals.memberFee') },
          { field: 'true_amount', title: t('withdrawals.actualAmount') },
          { field: 'status_format', title: t('withdrawals.transStatus') },
        ]],
        url: '/api/v1/proxy/withdrawals',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        parseData(res) {
          return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
        },
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#withdrawalsToolbar',
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

      form.on('submit(searchWithdrawals)', (formData) => {
        var where = formData.field || {}
        var dateRange = where.date_range || ''
        delete where.date_range
        delete where.quick_date
        if (dateRange) {
          where.create_time = dateRange
        }
        table.reload('withdrawalsTable', { where: where })
        return false
      })

      table.on('toolbar(withdrawalsTable)', (obj) => {
        if (obj.event === 'refresh') {
          table.reload('withdrawalsTable')
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
        <i class="layui-icon layui-icon-rmb"></i> {{ t('withdrawals.title') }}
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="withdrawalsSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>{{ t('withdrawals.accountName') }}</label>
            <input name="username" type="text" class="layui-input" :placeholder="t('withdrawals.enterAccountName')" />
          </div>
          <div class="data-search-field">
            <label>{{ t('withdrawals.transId') }}</label>
            <input name="serial_no" type="text" class="layui-input" :placeholder="t('withdrawals.enterTransId')" />
          </div>
          <div class="data-search-field">
            <label>{{ t('withdrawals.transStatus') }}</label>
            <select name="status">
              <option value="">{{ t('common.all') }}</option>
              <option value="0">{{ t('withdrawals.statusPending') }}</option>
              <option value="1">{{ t('withdrawals.statusComplete') }}</option>
              <option value="2">{{ t('withdrawals.statusProcessing') }}</option>
              <option value="3">{{ t('withdrawals.statusFailed') }}</option>
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
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchWithdrawals">
            <i class="layui-icon layui-icon-search"></i> {{ t('common.search') }}
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> {{ t('common.reset') }}
          </button>
        </div>
      </form>
    </div>

    <table id="withdrawalsTable" lay-filter="withdrawalsTable"></table>
  </div>
</template>
