<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'

const { createTemplate } = useLayuiTemplate()

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
          { field: 'username', title: 'Tên tài khoản' },
          { field: 'platform_id_name', title: 'Nhà cung cấp game' },
          { field: 't_bet_times', title: 'Số lần cược' },
          { field: 't_bet_amount', title: 'Tiền cược' },
          { field: 't_turnover', title: 'Tiền cược hợp lệ' },
          { field: 't_prize', title: 'Tiền thưởng' },
          { field: 't_win_lose', title: 'Thắng thua' },
        ]],
        data: [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#reportProviderToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Không có dữ liệu' },
      })

      form.render()
      initDateRange('input[name="date_range"]')

      form.on('select(quickDate)', (data) => {
        var input = document.querySelector('input[name="date_range"]')
        if (input) input.value = quickDateValue(data.value)
      })

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

</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-chart"></i> Báo cáo nhà cung cấp game
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="reportProviderSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Tên tài khoản</label>
            <input name="username" type="text" class="layui-input" placeholder="Nhập tên tài khoản" />
          </div>
          <div class="data-search-field">
            <label>Nhà cung cấp game</label>
            <select name="platform_id">
              <option value="">Tất cả</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>Chọn nhanh</label>
            <select name="quick_date" lay-filter="quickDate">
              <option value="">-- Chọn --</option>
              <option value="today">Hôm nay</option>
              <option value="yesterday">Hôm qua</option>
              <option value="7days">7 ngày qua</option>
              <option value="thisMonth">Tháng này</option>
              <option value="lastMonth">Tháng trước</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>Ngày bắt đầu - Ngày kết thúc</label>
            <input name="date_range" type="text" class="layui-input" placeholder="Ngày bắt đầu - Ngày kết thúc" readonly />
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
