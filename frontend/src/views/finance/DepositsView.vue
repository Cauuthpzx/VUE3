<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'
import depositsData from '@/data/deposits.json'

const { createTemplate } = useLayuiTemplate()

let tableIns = null

onMounted(() => {
  createTemplate('depositsToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = table.render({
        elem: '#depositsTable',
        id: 'depositsTable',
        cols: [[
          { field: 'username', title: 'Tên tài khoản' },
          { field: 'user_parent_format', title: 'Thuộc đại lý' },
          { field: 'amount', title: 'Số tiền' },
          { field: 'type', title: 'Loại hình giao dịch' },
          { field: 'status', title: 'Trạng thái giao dịch' },
          { field: 'create_time', title: 'Thời gian tạo đơn' },
        ]],
        data: depositsData.data || [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#depositsToolbar',
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

      form.on('submit(searchDeposits)', () => {
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

</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-rmb"></i> Nạp rút tiền
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="depositsSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Tên tài khoản</label>
            <input name="username" type="text" class="layui-input" placeholder="Nhập tên tài khoản" />
          </div>
          <div class="data-search-field">
            <label>Loại hình giao dịch</label>
            <select name="type">
              <option value="">Tất cả</option>
              <option value="1">Nạp tiền</option>
              <option value="2">Rút tiền</option>
            </select>
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
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchDeposits">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
        </div>
      </form>
    </div>

    <table id="depositsTable" lay-filter="depositsTable"></table>
  </div>
</template>
