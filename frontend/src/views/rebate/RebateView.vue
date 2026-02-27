<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'

const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()
let tableIns = null

onMounted(() => {
  createTemplate('rebateToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table'], (table) => {
      tableIns = renderTable(table, {
        elem: '#rebateTable',
        id: 'rebateTable',
        cols: [[
          { field: 'odds_11', title: 'Loại chơi', width: 130 },
          { field: 'odds_10', title: 'Cấp 10', width: 80 },
          { field: 'odds_9', title: 'Cấp 9', width: 80 },
          { field: 'odds_8', title: 'Cấp 8', width: 80 },
          { field: 'odds_7', title: 'Cấp 7', width: 80 },
          { field: 'odds_6', title: 'Cấp 6', width: 80 },
          { field: 'odds_5', title: 'Cấp 5', width: 80 },
          { field: 'odds_4', title: 'Cấp 4', width: 80 },
          { field: 'odds_3', title: 'Cấp 3', width: 80 },
          { field: 'odds_2', title: 'Cấp 2', width: 80 },
          { field: 'odds_1', title: 'Cấp 1', width: 80 },
        ]],
        data: [],
        page: false,
        toolbar: '#rebateToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      table.on('toolbar(rebateTable)', (obj) => {
        if (obj.event === 'refresh') {
          table.reload('rebateTable')
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
        <i class="layui-icon layui-icon-list"></i> Cấu hình tỷ lệ hoàn trả
      </h3>
    </div>

    <table id="rebateTable" lay-filter="rebateTable"></table>
  </div>
</template>
