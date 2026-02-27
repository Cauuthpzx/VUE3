<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { initDateRange } from '@/composables/useLayuiDate'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()
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
      tableIns = renderTable(table, {
        elem: '#membersTable',
        id: 'membersTable',
        cols: [[
          { field: '_agent_name', title: 'Đại lý' },
          { field: 'username', title: 'Hội viên' },
          { field: 'type_format', title: 'Loại hình hội viên' },
          { field: 'parent_user', title: 'Tài khoản đại lý' },
          { field: 'money', title: 'Số dư' },
          { field: 'deposit_count', title: 'Lần nạp' },
          { field: 'withdrawal_count', title: 'Lần rút' },
          { field: 'deposit_amount', title: 'Tổng tiền nạp' },
          { field: 'withdrawal_amount', title: 'Tổng tiền rút' },
          { field: 'login_time', title: 'Lần đăng nhập cuối' },
          { field: 'register_time', title: 'Thời gian đăng ký' },
          { field: 'status_format', title: 'Trạng thái' },
          { title: 'Thao tác', toolbar: '#membersRowBar' },
        ]],
        url: '/api/v1/proxy/members',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        headers: { Authorization: 'Bearer ' + authStore.accessToken },
        parseData(res) {
          return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
        },
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#membersToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      form.render()
      initDateRange('input[name="first_deposit_time"]', { value: '' })

      form.on('submit(searchMembers)', (data) => {
        table.reload('membersTable', {
          where: {
            username: data.field.username,
            status: data.field.status,
            sort_field: data.field.sort_field,
            sort_direction: data.field.sort_direction,
          }
        })
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
            <input name="first_deposit_time" type="text" class="layui-input" placeholder="Bắt đầu - Kết thúc" readonly />
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
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> Đặt lại
          </button>
        </div>
      </form>
    </div>

    <table id="membersTable" lay-filter="membersTable"></table>
  </div>
</template>
