<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'
import { useAuthStore } from '@/stores/auth'

const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()
const authStore = useAuthStore()
let tableIns = null

onMounted(() => {
  createTemplate('withdrawalsToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = renderTable(table, {
        elem: '#withdrawalsTable',
        id: 'withdrawalsTable',
        cols: [[
          { field: '_agent_name', title: 'Đại lý' },
          { field: 'serial_no', title: 'Mã giao dịch' },
          { field: 'create_time', title: 'Thời gian tạo đơn' },
          { field: 'username', title: 'Tên tài khoản' },
          { field: 'user_parent_format', title: 'Thuộc đại lý' },
          { field: 'amount', title: 'Số tiền' },
          { field: 'user_fee', title: 'Phí hội viên' },
          { field: 'true_amount', title: 'Số tiền thực tế' },
          { field: 'status_format', title: 'Trạng thái giao dịch' },
        ]],
        url: '/api/v1/proxy/withdrawals',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        headers: { Authorization: 'Bearer ' + authStore.accessToken },
        parseData(res) {
          return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
        },
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#withdrawalsToolbar',
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
        <i class="layui-icon layui-icon-rmb"></i> Lịch sử rút tiền
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="withdrawalsSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Tên tài khoản</label>
            <input name="username" type="text" class="layui-input" placeholder="Nhập tên tài khoản" />
          </div>
          <div class="data-search-field">
            <label>Mã giao dịch</label>
            <input name="serial_no" type="text" class="layui-input" placeholder="Nhập mã giao dịch" />
          </div>
          <div class="data-search-field">
            <label>Trạng thái giao dịch</label>
            <select name="status">
              <option value="">Tất cả</option>
              <option value="0">Chờ xử lí</option>
              <option value="1">Hoàn tất</option>
              <option value="2">Đang xử lí</option>
              <option value="3">Trạng thái không thành công</option>
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
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchWithdrawals">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> Đặt lại
          </button>
        </div>
      </form>
    </div>

    <table id="withdrawalsTable" lay-filter="withdrawalsTable"></table>
  </div>
</template>
