<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { initDateRange } from '@/composables/useLayuiDate'

const { createTemplate } = useLayuiTemplate()
let tableIns = null

onMounted(() => {
  createTemplate('invitesToolbar', `
    <button class="layui-btn layui-btn-xs" lay-event="add"><i class="layui-icon layui-icon-addition"></i>Thêm mã giới thiệu</button>
  `)
  createTemplate('invitesRowBar', `
    <button title="Copy đường link" class="layui-btn layui-btn-xs layui-btn-normal" lay-event="copy">Copy đường link</button>
    <button title="Cài đặt hoàn trả" class="layui-btn layui-btn-xs layui-btn-warm" lay-event="setting">Xem cài đặt</button>
    <button title="Mã QR" class="layui-btn layui-btn-xs layui-btn-danger" lay-event="qr">Mã QR</button>
    <button title="Chỉnh sửa" class="layui-btn layui-btn-xs" lay-event="edit">Chỉnh sửa</button>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = table.render({
        elem: '#invitesTable',
        id: 'invitesTable',
        cols: [[
          { field: 'invite_code', title: 'Mã giới thiệu' },
          { field: 'user_type', title: 'Loại hình giới thiệu' },
          { field: 'reg_count', title: 'Tổng số đã đăng ký' },
          { field: 'scope_reg_count', title: 'Số lượng người dùng đã đăng ký' },
          { field: 'recharge_count', title: 'Số người nạp tiền' },
          { field: 'first_recharge_count', title: 'Nạp đầu trong ngày' },
          { field: 'register_recharge_count', title: 'Nạp đầu trong ngày đăng kí' },
          { field: 'remark', title: 'Ghi chú', edit: 'text' },
          { field: 'create_time', title: 'Thời gian thêm vào' },
          { title: 'Thao tác', minWidth: 360, toolbar: '#invitesRowBar', fixed: 'right' },
        ]],
        data: [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#invitesToolbar',
        defaultToolbar: ['filter'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Không có dữ liệu' },
      })

      form.render()
      initDateRange('input[name="create_time"]')
      initDateRange('input[name="user_register_time"]')

      form.on('submit(searchInvites)', () => {
        return false
      })

      table.on('toolbar(invitesTable)', (obj) => {
        if (obj.event === 'add') {
          layui.layer.msg('Thêm mã giới thiệu')
        }
      })

      table.on('tool(invitesTable)', (obj) => {
        if (obj.event === 'copy') {
          layui.layer.msg('Đã sao chép đường link')
        } else if (obj.event === 'setting') {
          layui.layer.msg('Xem cài đặt hoàn trả')
        } else if (obj.event === 'qr') {
          layui.layer.msg('Mã QR')
        } else if (obj.event === 'edit') {
          layui.layer.msg('Chỉnh sửa mã giới thiệu')
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
        <i class="layui-icon layui-icon-link"></i> Mã giới thiệu
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="invitesSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Thời gian thêm vào</label>
            <input name="create_time" type="text" class="layui-input" placeholder="Thời gian bắt đầu - Thời gian kết thúc" readonly />
          </div>
          <div class="data-search-field">
            <label>Thời gian hội viên đăng nhập</label>
            <input name="user_register_time" type="text" class="layui-input" placeholder="Thời gian bắt đầu - Thời gian kết thúc" readonly />
          </div>
          <div class="data-search-field">
            <label>Mã giới thiệu</label>
            <input name="invite_code" type="text" class="layui-input" placeholder="Nhập đầy đủ mã giới thiệu" />
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
