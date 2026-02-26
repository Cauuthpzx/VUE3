<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'
import { createTemplate, removeTemplate } from '@/composables/useLayuiTemplate'

let tableIns = null

onMounted(() => {
  createTemplate('syncToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="add" title="Thêm mới"><i class="layui-icon layui-icon-add-1"></i></button>
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table'], (table) => {
      tableIns = table.render({
        elem: '#syncTable',
        id: 'syncTable',
        cols: [[
          { type: 'numbers', title: 'STT', width: 60 },
          { field: 'owner', title: 'Chủ sở hữu', width: 140 },
          { field: 'username', title: 'Username', width: 140 },
          {
            field: 'cookie_set', title: 'Cookie', width: 80, align: 'center',
            templet: (d) => d.cookie_set
              ? '<span style="color:#4CAF50;">&#10003;</span>'
              : '<span style="color:#999;">&#10007;</span>'
          },
          {
            field: 'is_active', title: 'Trạng thái', width: 100, align: 'center',
            templet: (d) => d.is_active
              ? '<span style="color:#4CAF50;">&#10003;</span>'
              : '<span style="color:#999;">&#10007;</span>'
          },
          { field: 'last_login_at', title: 'Đăng nhập cuối', width: 160 },
        ]],
        data: [],
        page: false,
        toolbar: '#syncToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      table.on('toolbar(syncTable)', (obj) => {
        if (obj.event === 'add') {
          layui.layer.msg('Thêm mới Agent')
        } else if (obj.event === 'refresh') {
          table.reload('syncTable')
        }
      })
    })
  })
})

onUnmounted(() => {
  removeTemplate('syncToolbar')
  tableIns = null
})
</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-refresh"></i> Quản lý đồng bộ Agent
      </h3>
    </div>

    <table id="syncTable" lay-filter="syncTable"></table>
  </div>
</template>
