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
  createTemplate('reportProviderToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = renderTable(table, {
        elem: '#reportProviderTable',
        id: 'reportProviderTable',
        cols: [[
          { field: '_agent_name', title: 'Đại lý' },
          { field: 'username', title: 'Tên tài khoản' },
          { field: 'platform_id_name', title: 'Nhà cung cấp game' },
          { field: 't_bet_times', title: 'Số lần cược' },
          { field: 't_bet_amount', title: 'Tiền cược' },
          { field: 't_turnover', title: 'Tiền cược hợp lệ' },
          { field: 't_prize', title: 'Tiền thưởng' },
          { field: 't_win_lose', title: 'Thắng thua' },
        ]],
        url: '/api/v1/proxy/report-third',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        headers: { Authorization: 'Bearer ' + authStore.accessToken },
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
        text: { none: 'Không có dữ liệu' },
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
            <label>Chọn thời gian</label>
            <input name="date_range" type="text" class="layui-input" placeholder="Bắt đầu - Kết thúc" readonly />
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchReportProvider">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> Đặt lại
          </button>
        </div>
      </form>
    </div>

    <table id="reportProviderTable" lay-filter="reportProviderTable"></table>

    <div v-if="totalData && Object.keys(totalData).length" class="data-total-bar">
      <h4 class="data-total-title">Tổng hợp toàn bộ dữ liệu</h4>
      <div class="data-total-fields">
        <div class="data-total-item">
          <span class="data-total-label">Số lần cược</span>
          <span class="data-total-value">{{ formatNumber(totalData.t_bet_times) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Tiền cược</span>
          <span class="data-total-value">{{ formatNumber(totalData.t_bet_amount) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Tiền cược hợp lệ</span>
          <span class="data-total-value">{{ formatNumber(totalData.t_turnover) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Tiền thưởng</span>
          <span class="data-total-value">{{ formatNumber(totalData.t_prize) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Thắng thua</span>
          <span class="data-total-value" :class="{ 'text-red': parseFloat(totalData.t_win_lose) < 0, 'text-green': parseFloat(totalData.t_win_lose) > 0 }">{{ formatNumber(totalData.t_win_lose) }}</span>
        </div>
        <div class="data-total-item">
          <span class="data-total-label">Số người cược</span>
          <span class="data-total-value">{{ formatNumber(totalData.username) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
