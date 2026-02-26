<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'
import { createTemplate, removeTemplate } from '@/composables/useLayuiTemplate'

let tableIns = null

onMounted(() => {
  createTemplate('reportLotteryToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = table.render({
        elem: '#reportLotteryTable',
        id: 'reportLotteryTable',
        cols: [[
          { type: 'numbers', title: 'STT', width: 60 },
          { field: '_agent_name', title: 'Agent', width: 120 },
          { field: 'username', title: 'Username', width: 140 },
          { field: 'user_parent_format', title: 'Tuyến trên', width: 120 },
          { field: 'bet_count', title: 'Số cược', width: 90 },
          { field: 'bet_amount', title: 'Tiền cược', width: 110 },
          { field: 'valid_amount', title: 'Tiền hợp lệ', width: 110 },
          { field: 'rebate_amount', title: 'Hoàn trả', width: 100 },
          { field: 'result', title: 'Kết quả', width: 100 },
          { field: 'win_lose', title: 'Thắng/Thua', width: 100 },
          { field: 'prize', title: 'Giải thưởng', width: 110 },
          { field: 'lottery_name', title: 'Tên Lottery', width: 130 },
        ]],
        data: [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#reportLotteryToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      form.render()

      form.on('submit(searchReportLottery)', () => {
        return false
      })

      table.on('toolbar(reportLotteryTable)', (obj) => {
        if (obj.event === 'refresh') {
          table.reload('reportLotteryTable')
        }
      })
    })
  })
})

onUnmounted(() => {
  removeTemplate('reportLotteryToolbar')
  tableIns = null
})
</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-chart"></i> Báo cáo Lottery
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="reportLotterySearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Username</label>
            <input name="username" type="text" class="layui-input" placeholder="Tìm username..." />
          </div>
          <div class="data-search-field">
            <label>Loại Lottery</label>
            <select name="lottery_id">
              <option value="">Tất cả</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>Ngày</label>
            <input name="date_range" type="text" class="layui-input" placeholder="dd/mm/yyyy - dd/mm/yyyy" />
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchReportLottery">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
        </div>
      </form>
    </div>

    <table id="reportLotteryTable" lay-filter="reportLotteryTable"></table>
  </div>
</template>
