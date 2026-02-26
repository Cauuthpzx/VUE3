<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'
import { createTemplate, removeTemplate } from '@/composables/useLayuiTemplate'

let tableIns = null

onMounted(() => {
  createTemplate('reportProviderToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = table.render({
        elem: '#reportProviderTable',
        id: 'reportProviderTable',
        cols: [[
          { type: 'numbers', title: 'STT', width: 60 },
          { field: '_agent_name', title: 'Agent', width: 120 },
          { field: 'username', title: 'Username', width: 140 },
          { field: 'platform_id_name', title: 'Nền tảng', width: 120 },
          { field: 't_bet_times', title: 'Số cược', width: 90 },
          { field: 't_bet_amount', title: 'Tiền cược', width: 110 },
          { field: 't_turnover', title: 'Doanh thu', width: 110 },
          { field: 't_prize', title: 'Giải thưởng', width: 110 },
          { field: 't_win_lose', title: 'Thắng/Thua', width: 100 },
        ]],
        data: [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#reportProviderToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      form.render()

      form.on('submit(searchReportProvider)', () => {
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

onUnmounted(() => {
  removeTemplate('reportProviderToolbar')
  tableIns = null
})
</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-chart"></i> Báo cáo Nhà cung cấp
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="reportProviderSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Username</label>
            <input name="username" type="text" class="layui-input" placeholder="Tìm username..." />
          </div>
          <div class="data-search-field">
            <label>Nền tảng</label>
            <select name="platform_id">
              <option value="">Tất cả</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>Ngày</label>
            <input name="date_range" type="text" class="layui-input" placeholder="dd/mm/yyyy - dd/mm/yyyy" />
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchReportProvider">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
        </div>
      </form>
    </div>

    <table id="reportProviderTable" lay-filter="reportProviderTable"></table>
  </div>
</template>
