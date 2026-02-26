<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'
import { createTemplate, removeTemplate } from '@/composables/useLayuiTemplate'

let tableIns = null

onMounted(() => {
  createTemplate('reportFundsToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = table.render({
        elem: '#reportFundsTable',
        id: 'reportFundsTable',
        cols: [[
          { type: 'numbers', title: 'STT', width: 60 },
          { field: '_agent_name', title: 'Agent', width: 120 },
          { field: 'username', title: 'Username', width: 140 },
          { field: 'user_parent_format', title: 'Tuyến trên', width: 120 },
          { field: 'deposit_count', title: 'Số nạp', width: 90 },
          { field: 'deposit_amount', title: 'Tiền nạp', width: 110 },
          { field: 'withdrawal_count', title: 'Số rút', width: 90 },
          { field: 'withdrawal_amount', title: 'Tiền rút', width: 110 },
          { field: 'charge_fee', title: 'Phí', width: 90 },
          { field: 'agent_commission', title: 'Hoa hồng', width: 100 },
          { field: 'promotion', title: 'Khuyến mãi', width: 100 },
          { field: 'third_rebate', title: 'Hoàn trả 3rd', width: 110 },
          { field: 'third_activity_amount', title: 'KM 3rd', width: 100 },
          { field: 'date', title: 'Ngày', width: 120 },
        ]],
        data: [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#reportFundsToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      form.render()

      form.on('submit(searchReportFunds)', () => {
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

onUnmounted(() => {
  removeTemplate('reportFundsToolbar')
  tableIns = null
})
</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-chart"></i> Báo cáo Tài chính
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="reportFundsSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Username</label>
            <input name="username" type="text" class="layui-input" placeholder="Tìm username..." />
          </div>
          <div class="data-search-field">
            <label>Ngày</label>
            <input name="date_range" type="text" class="layui-input" placeholder="dd/mm/yyyy - dd/mm/yyyy" />
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchReportFunds">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
        </div>
      </form>
    </div>

    <table id="reportFundsTable" lay-filter="reportFundsTable"></table>
  </div>
</template>
