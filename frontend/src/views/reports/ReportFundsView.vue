<script setup>
import { onMounted, nextTick, ref } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'
import { useAuthStore } from '@/stores/auth'

const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()
const authStore = useAuthStore()
const totalData = ref({})

let tableIns = null

function formatNumber(val) {
  if (val == null || val === '') return '0'
  var num = parseFloat(val)
  if (isNaN(num)) return val
  return num.toLocaleString('vi-VN', { minimumFractionDigits: 0, maximumFractionDigits: 4 })
}

onMounted(() => {
  createTemplate('reportFundsToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = renderTable(table, {
        elem: '#reportFundsTable',
        id: 'reportFundsTable',
        cols: [[
          { field: '_agent_name', title: 'Đại lý' },
          { field: 'username', title: 'Tên tài khoản' },
          { field: 'user_parent_format', title: 'Thuộc đại lý' },
          { field: 'deposit_count', title: 'Số lần nạp' },
          { field: 'deposit_amount', title: 'Số tiền nạp', sort: true },
          { field: 'withdrawal_count', title: 'Số lần rút' },
          { field: 'withdrawal_amount', title: 'Số tiền rút' },
          { field: 'charge_fee', title: 'Phí dịch vụ' },
          { field: 'agent_commission', title: 'Hoa hồng đại lý' },
          { field: 'promotion', title: 'Ưu đãi' },
          { field: 'third_rebate', title: 'Hoàn trả bên thứ 3' },
          { field: 'third_activity_amount', title: 'Tiền thưởng từ bên thứ 3' },
          { field: 'date', title: 'Thời gian' },
        ]],
        url: '/api/v1/proxy/report-funds',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        headers: { Authorization: 'Bearer ' + authStore.accessToken },
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
        text: { none: 'Không có dữ liệu' },
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
            <label>Chọn thời gian</label>
            <input name="date_range" type="text" class="layui-input" placeholder="Bắt đầu - Kết thúc" readonly />
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchReportFunds">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> Đặt lại
          </button>
        </div>
      </form>
    </div>

    <table id="reportFundsTable" lay-filter="reportFundsTable"></table>

    <div v-if="totalData && Object.keys(totalData).length" class="data-total-bar">
      <h4 class="data-total-title">Tổng hợp toàn bộ dữ liệu</h4>
      <div class="data-total-fields">
        <div class="data-total-item">
          <span class="data-total-label">Số lần nạp</span>
          <span class="data-total-value">{{ formatNumber(totalData.deposit_count) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Số tiền nạp</span>
          <span class="data-total-value">{{ formatNumber(totalData.deposit_amount) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Số lần rút</span>
          <span class="data-total-value">{{ formatNumber(totalData.withdrawal_count) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Số tiền rút</span>
          <span class="data-total-value">{{ formatNumber(totalData.withdrawal_amount) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Phí dịch vụ</span>
          <span class="data-total-value">{{ formatNumber(totalData.charge_fee) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Hoa hồng đại lý</span>
          <span class="data-total-value">{{ formatNumber(totalData.agent_commission) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Ưu đãi</span>
          <span class="data-total-value">{{ formatNumber(totalData.promotion) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Hoàn trả bên thứ 3</span>
          <span class="data-total-value">{{ formatNumber(totalData.third_rebate) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Tiền thưởng bên thứ 3</span>
          <span class="data-total-value">{{ formatNumber(totalData.third_activity_amount) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
