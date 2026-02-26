<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'

const { createTemplate } = useLayuiTemplate()
let tableIns = null

onMounted(() => {
  createTemplate('tiersToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="add" title="Thêm mới"><i class="layui-icon layui-icon-add-1"></i></button>
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table'], (table) => {
      tableIns = table.render({
        elem: '#tiersTable',
        id: 'tiersTable',
        cols: [[
          { type: 'numbers', title: 'STT', width: 60 },
          { field: 'name', title: 'Tên cấp bậc', minWidth: 200 },
          { field: 'created_at', title: 'Ngày tạo', width: 200 },
        ]],
        data: [],
        page: false,
        toolbar: '#tiersToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      table.on('toolbar(tiersTable)', (obj) => {
        if (obj.event === 'add') {
          layui.layer.msg('Thêm cấp bậc mới')
        } else if (obj.event === 'refresh') {
          table.reload('tiersTable')
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
        <i class="layui-icon layui-icon-rate"></i> Quản lý cấp bậc
      </h3>
    </div>

    <table id="tiersTable" lay-filter="tiersTable"></table>
  </div>
</template>
