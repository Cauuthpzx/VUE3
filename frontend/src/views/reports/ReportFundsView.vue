<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'

const { createTemplate } = useLayuiTemplate()

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
          { field: 'username', title: 'Tên tài khoản', fixed: 'left', width: 150 },
          { field: 'user_parent_format', title: 'Thuộc đại lý', width: 150 },
          { field: 'deposit_count', title: 'Số lần nạp', width: 160 },
          { field: 'deposit_amount', title: 'Số tiền nạp', minWidth: 150, sort: true },
          { field: 'withdrawal_count', title: 'Số lần rút', minWidth: 150 },
          { field: 'withdrawal_amount', title: 'Số tiền rút', minWidth: 160 },
          { field: 'charge_fee', title: 'Phí dịch vụ', minWidth: 150 },
          { field: 'agent_commission', title: 'Hoa hồng đại lý', minWidth: 150 },
          { field: 'promotion', title: 'Ưu đãi', minWidth: 150 },
          { field: 'third_rebate', title: 'Hoàn trả bên thứ 3', minWidth: 150 },
          { field: 'third_activity_amount', title: 'Tiền thưởng từ bên thứ 3', minWidth: 150 },
          { field: 'date', title: 'Thời gian', minWidth: 160, fixed: 'right' },
        ]],
        data: [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#reportFundsToolbar',
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

</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-chart"></i> Báo cáo tài chính
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="reportFundsSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Tên tài khoản</label>
            <input name="username" type="text" class="layui-input" placeholder="Nhập tên tài khoản" />
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
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchReportFunds">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
        </div>
      </form>
    </div>

    <table id="reportFundsTable" lay-filter="reportFundsTable"></table>
  </div>
</template>
