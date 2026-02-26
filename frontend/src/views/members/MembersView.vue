<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'

const { createTemplate } = useLayuiTemplate()
let tableIns = null

onMounted(() => {
  createTemplate('membersToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="addUser"><i class="layui-icon layui-icon-addition"></i>Thêm hội viên</button>
      <button class="layui-btn layui-btn-xs" lay-event="addAgent"><i class="layui-icon layui-icon-addition"></i>Đại lý mới thêm</button>
    </div>
  `)
  createTemplate('membersRowBar', `
    <button class="layui-btn layui-btn-xs" lay-event="detail">Cài đặt hoàn trả</button>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = table.render({
        elem: '#membersTable',
        id: 'membersTable',
        cols: [[
          { field: 'username', title: 'Hội viên', width: 150, fixed: 'left' },
          { field: 'type_format', title: 'Loại hình hội viên', width: 100 },
          { field: 'parent_user', title: 'Tài khoản đại lý', width: 150 },
          { field: 'money', title: 'Số dư', width: 150 },
          { field: 'deposit_count', title: 'Lần nạp', width: 100 },
          { field: 'withdrawal_count', title: 'Lần rút', width: 100 },
          { field: 'deposit_amount', title: 'Tổng tiền nạp', width: 100 },
          { field: 'withdrawal_amount', title: 'Tổng tiền rút', width: 100 },
          { field: 'login_time', title: 'Lần đăng nhập cuối', width: 160 },
          { field: 'register_time', title: 'Thời gian đăng ký', width: 160 },
          { field: 'status_format', title: 'Trạng thái', width: 100 },
          { fixed: 'right', title: 'Thao tác', width: 130, toolbar: '#membersRowBar' },
        ]],
        data: [],
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#membersToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      form.render()

      form.on('submit(searchMembers)', () => {
        return false
      })

      table.on('toolbar(membersTable)', (obj) => {
        if (obj.event === 'addUser') {
          layui.layer.msg('Thêm hội viên')
        } else if (obj.event === 'addAgent') {
          layui.layer.msg('Đại lý mới thêm')
        }
      })

      table.on('tool(membersTable)', (obj) => {
        if (obj.event === 'detail') {
          layui.layer.msg('Cài đặt hoàn trả')
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
        <i class="layui-icon layui-icon-friends"></i> Quản lí hội viên thuộc cấp
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="membersSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>Tên tài khoản</label>
            <input name="username" type="text" class="layui-input" placeholder="Nhập tên tài khoản" />
          </div>
          <div class="data-search-field">
            <label>Thời gian nạp đầu</label>
            <input name="first_deposit_time" type="text" class="layui-input" placeholder="Thời gian bắt đầu - Thời gian kết thúc" readonly />
          </div>
          <div class="data-search-field">
            <label>Trạng thái</label>
            <select name="status">
              <option value="">Chọn</option>
              <option value="0">Chưa đánh giá</option>
              <option value="1">Bình thường</option>
              <option value="2">Đóng băng</option>
              <option value="3">Khóa</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>Sắp xếp theo trường</label>
            <select name="sort_field">
              <option value="">Chọn</option>
              <option value="money">Số dư</option>
              <option value="login_time">Lần đăng nhập cuối</option>
              <option value="register_time">Thời gian đăng ký</option>
              <option value="deposit_money">Tổng tiền nạp</option>
              <option value="withdrawal_money">Tổng tiền rút</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>Sắp xếp theo hướng</label>
            <select name="sort_direction">
              <option value="desc">Từ lớn đến bé</option>
              <option value="asc">Từ bé đến lớn</option>
            </select>
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchMembers">
            <i class="layui-icon layui-icon-search"></i> Tìm kiếm
          </button>
        </div>
      </form>
    </div>

    <table id="membersTable" lay-filter="membersTable"></table>
  </div>
</template>
