<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'
import { useAuthStore } from '@/stores/auth'

const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()
const authStore = useAuthStore()
let tableIns = null

onMounted(() => {
  createTemplate('betThirdPartyToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = renderTable(table, {
        elem: '#betThirdPartyTable',
        id: 'betThirdPartyTable',
        cols: [[
          { field: '_agent_name', title: 'Đại lý' },
          { field: 'serial_no', title: 'Mã giao dịch' },
          { field: 'platform_id_name', title: 'Nhà cung cấp game bên thứ 3' },
          { field: 'platform_username', title: 'Tên tài khoản thuộc nhà cái' },
          { field: 'c_name', title: 'Loại hình trò chơi' },
          { field: 'game_name', title: 'Tên trò chơi bên thứ 3' },
          { field: 'bet_amount', title: 'Tiền cược' },
          { field: 'turnover', title: 'Tiền cược hợp lệ' },
          { field: 'prize', title: 'Tiền thưởng' },
          { field: 'win_lose', title: 'Thắng thua' },
          { field: 'bet_time', title: 'Thời gian cược' },
        ]],
        url: '/api/v1/proxy/bet-orders',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        headers: { Authorization: 'Bearer ' + authStore.accessToken },
        parseData(res) {
          return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
        },
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#betThirdPartyToolbar',
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

      form.on('submit(searchBetThirdParty)', (formData) => {
        var where = formData.field || {}
        var dateRange = where.date_range || ''
        delete where.date_range
        delete where.quick_date
        if (dateRange) {
          where.bet_time = dateRange
        }
        table.reload('betThirdPartyTable', { where: where })
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

</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-game"></i> Đơn cược bên thứ 3
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="betThirdPartySearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Tên tài khoản</label>
            <input name="username" type="text" class="layui-input" placeholder="Nhập tên tài khoản" />
          </div>
          <div class="data-search-field">
            <label>Mã giao dịch</label>
            <input name="serial_no" type="text" class="layui-input" placeholder="Nhập mã giao dịch" />
          </div>
          <div class="data-search-field">
            <label>Tên tài khoản thuộc nhà cái</label>
            <input name="platform_username" type="text" class="layui-input" placeholder="Nhập tên tài khoản nhà cái" />
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
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchBetThirdParty">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> Đặt lại
          </button>
        </div>
      </form>
    </div>

    <table id="betThirdPartyTable" lay-filter="betThirdPartyTable"></table>
  </div>
</template>
