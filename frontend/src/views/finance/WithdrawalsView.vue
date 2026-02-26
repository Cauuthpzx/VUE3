<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'
import { createTemplate, removeTemplate } from '@/composables/useLayuiTemplate'

let tableIns = null

onMounted(() => {
  createTemplate('withdrawalsToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = table.render({
        elem: '#withdrawalsTable',
        id: 'withdrawalsTable',
        cols: [[
          { type: 'numbers', title: 'STT', width: 60 },
          { field: '_agent_name', title: 'Agent', width: 120 },
          { field: 'serial_no', title: 'Mã GD', width: 140 },
          { field: 'create_time', title: 'Thời gian', width: 160 },
          { field: 'username', title: 'Username', width: 140 },
          { field: 'user_parent_format', title: 'Tuyến trên', width: 120 },
          { field: 'amount', title: 'Số tiền', width: 110 },
          { field: 'user_fee', title: 'Phí', width: 90 },
          { field: 'true_amount', title: 'Thực nhận', width: 110 },
          { field: 'status_format', title: 'Trạng thái', width: 100 },
        ]],
        data: [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#withdrawalsToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      form.render()

      form.on('submit(searchWithdrawals)', () => {
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

onUnmounted(() => {
  removeTemplate('withdrawalsToolbar')
  tableIns = null
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
            <label>Username</label>
            <input name="username" type="text" class="layui-input" placeholder="Tìm username..." />
          </div>
          <div class="data-search-field">
            <label>Mã giao dịch</label>
            <input name="serial_no" type="text" class="layui-input" placeholder="Mã giao dịch..." />
          </div>
          <div class="data-search-field">
            <label>Trạng thái</label>
            <select name="status">
              <option value="">Tất cả</option>
              <option value="0">Chờ xử lý</option>
              <option value="1">Hoàn thành</option>
              <option value="2">Đang xử lý</option>
              <option value="3">Thất bại</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>Ngày</label>
            <input name="date_range" type="text" class="layui-input" placeholder="dd/mm/yyyy - dd/mm/yyyy" />
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchWithdrawals">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
        </div>
      </form>
    </div>

    <table id="withdrawalsTable" lay-filter="withdrawalsTable"></table>
  </div>
</template>
