<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'
import { createTemplate, removeTemplate } from '@/composables/useLayuiTemplate'

let tableIns = null

onMounted(() => {
  createTemplate('membersToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="add" title="Thêm mới"><i class="layui-icon layui-icon-add-1"></i></button>
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = table.render({
        elem: '#membersTable',
        id: 'membersTable',
        cols: [[
          { type: 'numbers', title: 'STT', width: 60 },
          { field: '_agent_name', title: 'Agent', width: 120 },
          { field: 'username', title: 'Username', width: 140 },
          { field: 'type_format', title: 'Loại', width: 80 },
          { field: 'parent_user', title: 'Tuyến trên', width: 120 },
          { field: 'money', title: 'Số dư', width: 110 },
          { field: 'deposit_count', title: 'Số lần nạp', width: 100 },
          { field: 'withdrawal_count', title: 'Số lần rút', width: 100 },
          { field: 'deposit_amount', title: 'Tổng nạp', width: 110 },
          { field: 'withdrawal_amount', title: 'Tổng rút', width: 110 },
          { field: 'login_time', title: 'Đăng nhập cuối', width: 160 },
          { field: 'status_format', title: 'Trạng thái', width: 100 },
        ]],
        data: [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#membersToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      form.render()

      form.on('submit(searchMembers)', () => {
        return false
      })

      table.on('toolbar(membersTable)', (obj) => {
        if (obj.event === 'add') {
          layui.layer.msg('Thêm mới thành viên')
        } else if (obj.event === 'refresh') {
          table.reload('membersTable')
        }
      })
    })
  })
})

onUnmounted(() => {
  removeTemplate('membersToolbar')
  tableIns = null
})
</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-friends"></i> Thành viên
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="membersSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Username</label>
            <input name="username" type="text" class="layui-input" placeholder="Tìm username..." />
          </div>
          <div class="data-search-field">
            <label>Trạng thái</label>
            <select name="status">
              <option value="">Tất cả</option>
              <option value="1">Bình thường</option>
              <option value="2">Đóng băng</option>
              <option value="3">Khóa</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>Sắp xếp</label>
            <select name="sort_field">
              <option value="">Mặc định</option>
              <option value="money">Số dư</option>
              <option value="login_time">Đăng nhập cuối</option>
              <option value="register_time">Ngày đăng ký</option>
              <option value="deposit_money">Tổng nạp</option>
              <option value="withdrawal_money">Tổng rút</option>
            </select>
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchMembers">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
        </div>
      </form>
    </div>

    <table id="membersTable" lay-filter="membersTable"></table>
  </div>
</template>
