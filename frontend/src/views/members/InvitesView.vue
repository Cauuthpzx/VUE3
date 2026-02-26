<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'
import { createTemplate, removeTemplate } from '@/composables/useLayuiTemplate'

let tableIns = null

onMounted(() => {
  createTemplate('invitesToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="add" title="Thêm mới"><i class="layui-icon layui-icon-add-1"></i></button>
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)
  createTemplate('invitesRowBar', `
    <button class="layui-btn layui-btn-xs" lay-event="copy">Sao chép</button>
    <button class="layui-btn layui-btn-xs layui-btn-normal" lay-event="setting">Cài đặt</button>
    <button class="layui-btn layui-btn-xs layui-btn-warm" lay-event="qr">QR Code</button>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = table.render({
        elem: '#invitesTable',
        id: 'invitesTable',
        cols: [[
          { type: 'numbers', title: 'STT', width: 60 },
          { field: '_agent_name', title: 'Agent', width: 120 },
          { field: 'invite_code', title: 'Mã mời', width: 140 },
          { field: 'user_type', title: 'Loại', width: 80 },
          { field: 'reg_count', title: 'Số đăng ký', width: 100 },
          { field: 'scope_reg_count', title: 'Phạm vi ĐK', width: 100 },
          { field: 'recharge_count', title: 'Số nạp tiền', width: 100 },
          { field: 'first_recharge_count', title: 'Nạp lần đầu', width: 100 },
          { field: 'register_recharge_count', title: 'ĐK & nạp', width: 100 },
          { field: 'remark', title: 'Ghi chú', width: 120 },
          { field: 'create_time', title: 'Ngày tạo', width: 160 },
          { title: 'Thao tác', width: 200, align: 'center', toolbar: '#invitesRowBar' },
        ]],
        data: [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#invitesToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      form.render()

      form.on('submit(searchInvites)', () => {
        return false
      })

      table.on('toolbar(invitesTable)', (obj) => {
        if (obj.event === 'add') {
          layui.layer.msg('Thêm mã mời mới')
        } else if (obj.event === 'refresh') {
          table.reload('invitesTable')
        }
      })

      table.on('tool(invitesTable)', (obj) => {
        if (obj.event === 'copy') {
          layui.layer.msg('Đã sao chép')
        } else if (obj.event === 'setting') {
          layui.layer.msg('Cài đặt')
        } else if (obj.event === 'qr') {
          layui.layer.msg('QR Code')
        }
      })
    })
  })
})

onUnmounted(() => {
  removeTemplate('invitesToolbar')
  removeTemplate('invitesRowBar')
  tableIns = null
})
</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-link"></i> Mã mời
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="invitesSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Mã mời</label>
            <input name="invite_code" type="text" class="layui-input" placeholder="Tìm mã mời..." />
          </div>
          <div class="data-search-field">
            <label>Loại người dùng</label>
            <select name="user_type">
              <option value="">Tất cả</option>
              <option value="1">Thường</option>
              <option value="3">Mời</option>
            </select>
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchInvites">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
        </div>
      </form>
    </div>

    <table id="invitesTable" lay-filter="invitesTable"></table>
  </div>
</template>
