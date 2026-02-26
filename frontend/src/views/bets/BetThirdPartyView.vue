<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'
import { createTemplate, removeTemplate } from '@/composables/useLayuiTemplate'

let tableIns = null

onMounted(() => {
  createTemplate('betThirdPartyToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = table.render({
        elem: '#betThirdPartyTable',
        id: 'betThirdPartyTable',
        cols: [[
          { type: 'numbers', title: 'STT', width: 60 },
          { field: '_agent_name', title: 'Agent', width: 120 },
          { field: 'serial_no', title: 'Mã GD', width: 140 },
          { field: 'platform_id_name', title: 'Nền tảng', width: 120 },
          { field: 'platform_username', title: 'Username NTT', width: 130 },
          { field: 'c_name', title: 'Tên game', width: 120 },
          { field: 'game_name', title: 'Game', width: 120 },
          { field: 'bet_amount', title: 'Tiền cược', width: 100 },
          { field: 'turnover', title: 'Doanh thu', width: 100 },
          { field: 'prize', title: 'Giải thưởng', width: 100 },
          { field: 'win_lose', title: 'Thắng/Thua', width: 100 },
          { field: 'bet_time', title: 'Thời gian', width: 160 },
        ]],
        data: [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#betThirdPartyToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      form.render()

      form.on('submit(searchBetThirdParty)', () => {
        return false
      })

      table.on('toolbar(betThirdPartyTable)', (obj) => {
        if (obj.event === 'refresh') {
          table.reload('betThirdPartyTable')
        }
      })
    })
  })
})

onUnmounted(() => {
  removeTemplate('betThirdPartyToolbar')
  tableIns = null
})
</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-game"></i> Cược bên thứ ba
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="betThirdPartySearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Username</label>
            <input name="username" type="text" class="layui-input" placeholder="Tìm username..." />
          </div>
          <div class="data-search-field">
            <label>Mã GD</label>
            <input name="serial_no" type="text" class="layui-input" placeholder="Serial no..." />
          </div>
          <div class="data-search-field">
            <label>Username nền tảng</label>
            <input name="platform_username" type="text" class="layui-input" placeholder="Platform username..." />
          </div>
          <div class="data-search-field">
            <label>Ngày</label>
            <input name="date_range" type="text" class="layui-input" placeholder="dd/mm/yyyy - dd/mm/yyyy" />
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchBetThirdParty">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
        </div>
      </form>
    </div>

    <table id="betThirdPartyTable" lay-filter="betThirdPartyTable"></table>
  </div>
</template>
