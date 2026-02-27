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
  createTemplate('depositsToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="${t('common.refresh')}"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)
}

function getCols() {
  return [[
    { field: '_agent_name', title: t('common.staff'), width: 110 },
    { field: 'username', title: t('deposits.accountName') },
    { field: 'user_parent_format', title: t('deposits.belongAgent') },
    { field: 'amount', title: t('deposits.amount') },
    { field: 'type', title: t('deposits.transType') },
    { field: 'status', title: t('deposits.transStatus') },
    { field: 'create_time', title: t('deposits.createTime') },
  ]]
}

function initTable(table) {
  initTemplates()
  renderTable(table, {
    elem: '#depositsTable',
    id: 'depositsTable',
    cols: getCols(),
    url: '/api/v1/proxy/deposits',
    method: 'post',
    contentType: 'application/x-www-form-urlencoded',
    parseData(res) {
      return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
    },
    page: { limit: 10, limits: [10, 50, 100, 200] },
    toolbar: '#depositsToolbar',
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

      form.on('submit(searchDeposits)', (formData) => {
        var where = formData.field || {}
        var dateRange = where.date_range || ''
        delete where.date_range
        delete where.quick_date
        if (dateRange) {
          where.create_time = dateRange
        }
        table.reload('depositsTable', { where: where })
        return false
      })

      table.on('toolbar(depositsTable)', (obj) => {
        if (obj.event === 'refresh') {
          table.reload('depositsTable')
        }
      })
    })
  })
})

onLocaleChange(() => {
  initTemplates()
  layui.use(['table'], (table) => {
    reloadTable(table, 'depositsTable', {
      cols: getCols(),
      toolbar: '#depositsToolbar',
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
        <i class="layui-icon layui-icon-rmb"></i> {{ t('deposits.title') }}
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="depositsSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>{{ t('deposits.accountName') }}</label>
            <input name="username" type="text" class="layui-input" :placeholder="t('deposits.enterAccountName')" />
          </div>
          <div class="data-search-field">
            <label>{{ t('deposits.transType') }}</label>
            <select name="type">
              <option value="">{{ t('common.all') }}</option>
              <option value="1">{{ t('deposits.typeDeposit') }}</option>
              <option value="2">{{ t('deposits.typeWithdraw') }}</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>{{ t('deposits.transStatus') }}</label>
            <select name="status">
              <option value="">{{ t('common.all') }}</option>
              <option value="0">{{ t('deposits.statusPending') }}</option>
              <option value="1">{{ t('deposits.statusComplete') }}</option>
              <option value="2">{{ t('deposits.statusProcessing') }}</option>
              <option value="3">{{ t('deposits.statusFailed') }}</option>
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
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchDeposits">
            <i class="layui-icon layui-icon-search"></i> {{ t('common.search') }}
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> {{ t('common.reset') }}
          </button>
        </div>
      </form>
    </div>

    <table id="depositsTable" lay-filter="depositsTable"></table>
  </div>
</template>
