<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'
import { createTemplate, removeTemplate } from '@/composables/useLayuiTemplate'

let tableIns = null

onMounted(() => {
  createTemplate('accountToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="add" title="Thêm tài khoản"><i class="layui-icon layui-icon-add-1"></i></button>
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)
  createTemplate('accountRowBar', `
    <button class="layui-btn layui-btn-xs layui-btn-warm" lay-event="edit">Sửa</button>
    <button class="layui-btn layui-btn-xs layui-btn-normal" lay-event="perm">Quyền</button>
    <button class="layui-btn layui-btn-xs layui-btn-danger" lay-event="del">Xóa</button>
  `)

  nextTick(() => {
    layui.use(['table'], (table) => {
      tableIns = table.render({
        elem: '#accountTable',
        id: 'accountTable',
        cols: [[
          { type: 'numbers', title: 'STT', width: 60 },
          { field: 'name', title: 'Tên', width: 140 },
          { field: 'username', title: 'Username', width: 140 },
          { field: 'email', title: 'Email', width: 200 },
          {
            field: 'role', title: 'Vai trò', width: 120,
            templet: (d) => {
              const colorMap = { ADMINHUB: '#FF5722', MODHUB: '#2196F3', USERHUB: '#4CAF50' }
              const c = colorMap[d.role] || '#999'
              return '<span style="color:' + c + ';font-weight:bold;">' + (d.role || '') + '</span>'
            }
          },
          {
            field: 'is_active', title: 'Trạng thái', width: 100,
            templet: (d) => d.is_active
              ? '<span style="color:#4CAF50;">Hoạt động</span>'
              : '<span style="color:#999;">Khóa</span>'
          },
          { field: 'created_at', title: 'Ngày tạo', width: 160 },
          { title: 'Thao tác', width: 220, align: 'center', toolbar: '#accountRowBar' },
        ]],
        data: [],
        page: false,
        toolbar: '#accountToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      table.on('toolbar(accountTable)', (obj) => {
        if (obj.event === 'add') {
          layui.layer.msg('Thêm tài khoản mới')
        } else if (obj.event === 'refresh') {
          table.reload('accountTable')
        }
      })

      table.on('tool(accountTable)', (obj) => {
        if (obj.event === 'edit') {
          layui.layer.msg('Sửa tài khoản')
        } else if (obj.event === 'perm') {
          layui.layer.msg('Phân quyền')
        } else if (obj.event === 'del') {
          layui.layer.confirm('Xác nhận xóa tài khoản?', { icon: 3 }, (index) => {
            layui.layer.close(index)
            layui.layer.msg('Đã xóa')
          })
        }
      })
    })
  })
})

onUnmounted(() => {
  removeTemplate('accountToolbar')
  removeTemplate('accountRowBar')
  tableIns = null
})
</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-group"></i> Quản lý tài khoản & Phân quyền
      </h3>
    </div>

    <table id="accountTable" lay-filter="accountTable"></table>
  </div>
</template>
