<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()
let tableIns = null

onMounted(() => {
  createTemplate('betsToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = renderTable(table, {
        elem: '#betsTable',
        id: 'betsTable',
        cols: [[
          { field: '_agent_name', title: 'Đại lý' },
          { field: 'serial_no', title: 'Mã giao dịch' },
          { field: 'username', title: 'Tên người dùng' },
          { field: 'create_time', title: 'Thời gian cược' },
          { field: 'lottery_name', title: 'Trò chơi' },
          { field: 'play_type_name', title: 'Loại trò chơi' },
          { field: 'play_name', title: 'Cách chơi' },
          { field: 'issue', title: 'Kỳ' },
          { field: 'content', title: 'Thông tin cược' },
          { field: 'money', title: 'Tiền cược' },
          { field: 'rebate_amount', title: 'Tiền hoàn trả' },
          { field: 'result', title: 'Thắng thua' },
          { field: 'status_text', title: 'Trạng thái' },
        ]],
        url: '/api/v1/proxy/bets',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        headers: { Authorization: 'Bearer ' + authStore.accessToken },
        parseData(res) {
          return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
        },
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#betsToolbar',
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

      form.on('submit(searchBets)', (data) => {
        var whereParams = {
          username: data.field.username,
          serial_no: data.field.serial_no,
          lottery_id: data.field.lottery_id,
          status: data.field.status,
        }
        if (data.field.date_range) {
          whereParams.create_time = data.field.date_range
        }
        delete whereParams.quick_date
        table.reload('betsTable', { where: whereParams })
        return false
      })

      table.on('toolbar(betsTable)', (obj) => {
        if (obj.event === 'refresh') {
          table.reload('betsTable')
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
        <i class="layui-icon layui-icon-game"></i> Đơn cược xổ số
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="betsSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Tên người dùng</label>
            <input name="username" type="text" class="layui-input" placeholder="Nhập tên người dùng" />
          </div>
          <div class="data-search-field">
            <label>Mã giao dịch</label>
            <input name="serial_no" type="text" class="layui-input" placeholder="Nhập mã giao dịch" />
          </div>
          <div class="data-search-field">
            <label>Trò chơi</label>
            <select name="lottery_id">
              <option value="">Tất cả</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>Trạng thái</label>
            <select name="status">
              <option value="">Tất cả</option>
              <option value="-9">Chưa thanh toán</option>
              <option value="1">Thắng</option>
              <option value="-1">Thua</option>
              <option value="2">Hòa</option>
              <option value="3">Hủy (người dùng)</option>
              <option value="4">Hủy (hệ thống)</option>
              <option value="5">Đơn cược bất thường</option>
              <option value="6">Chưa thanh toán (khôi phục thủ công)</option>
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
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchBets">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> Đặt lại
          </button>
        </div>
      </form>
    </div>

    <table id="betsTable" lay-filter="betsTable"></table>
  </div>
</template>
