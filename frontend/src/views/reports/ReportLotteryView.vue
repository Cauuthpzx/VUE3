<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { initDateRange, quickDateValue } from '@/composables/useLayuiDate'
import reportLotteryData from '@/data/report_lottery.json'

const { createTemplate } = useLayuiTemplate()

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
          { field: 'username', title: 'Tên tài khoản', fixed: 'left', width: 150 },
          { field: 'user_parent_format', title: 'Thuộc đại lý', width: 150 },
          { field: 'bet_count', title: 'Số lần cược', minWidth: 150 },
          { field: 'bet_amount', title: 'Tiền cược', minWidth: 150 },
          { field: 'valid_amount', title: 'Tiền cược hợp lệ (trừ cược hoà)', minWidth: 160 },
          { field: 'rebate_amount', title: 'Hoàn trả', minWidth: 150 },
          { field: 'result', title: 'Thắng thua', minWidth: 150 },
          { field: 'win_lose', title: 'Kết quả thắng thua (không gồm hoàn trả)', minWidth: 180 },
          { field: 'prize', title: 'Tiền trúng', minWidth: 150 },
          { field: 'lottery_name', title: 'Tên loại xổ', width: 160, fixed: 'right' },
        ]],
        data: reportLotteryData.data || [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#reportLotteryToolbar',
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

</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-chart"></i> Báo cáo xổ số
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="reportLotterySearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Tên tài khoản</label>
            <input name="username" type="text" class="layui-input" placeholder="Nhập tên tài khoản" />
          </div>
          <div class="data-search-field">
            <label>Loại xổ số</label>
            <select name="lottery_id">
              <option value="">Tất cả</option>
            </select>
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
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchReportLottery">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
        </div>
      </form>
    </div>

    <table id="reportLotteryTable" lay-filter="reportLotteryTable"></table>
  </div>
</template>
