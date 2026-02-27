<script setup>
import { onMounted, onUnmounted, nextTick, ref } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { useAuthStore } from '@/stores/auth'
import { usersApi } from '@/api/users'
import { authApi } from '@/api/auth'

const authStore = useAuthStore()
const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()

let tableIns = null

/* ===== STATE ===== */
const showModal = ref(false)
const editingUser = ref(null)
const form = ref({ name: '', username: '', email: '', password: '' })
const formError = ref('')

/* ===== LOAD DATA ===== */
async function loadUsers() {
  try {
    const { data } = await usersApi.list({ skip: 0, limit: 100 })
    const users = Array.isArray(data) ? data : (data.data || [])
    layui.use(['table'], (table) => {
      table.reload('accountTable', { data: users })
    })
  } catch (e) {
    console.error('Failed to load users:', e)
  }
}

/* ===== USER CRUD ===== */
function openAdd() {
  editingUser.value = null
  form.value = { name: '', username: '', email: '', password: '' }
  formError.value = ''
  showModal.value = true
  nextTick(() => layui.use(['form'], (f) => f.render()))
}

function openEdit(user) {
  editingUser.value = user
  form.value = { name: user.name, username: user.username, email: user.email, password: '' }
  formError.value = ''
  showModal.value = true
  nextTick(() => layui.use(['form'], (f) => f.render()))
}

async function saveUser() {
  formError.value = ''
  if (!form.value.name.trim()) { formError.value = 'Vui lòng nhập họ tên'; return }
  if (!form.value.username.trim()) { formError.value = 'Vui lòng nhập username'; return }
  if (!form.value.email.trim()) { formError.value = 'Vui lòng nhập email'; return }

  try {
    if (editingUser.value) {
      const payload = {}
      if (form.value.name !== editingUser.value.name) payload.name = form.value.name
      if (form.value.username !== editingUser.value.username) payload.username = form.value.username
      if (form.value.email !== editingUser.value.email) payload.email = form.value.email
      await usersApi.update(editingUser.value.id, payload)
      layui.layer.msg('Cập nhật thành công', { icon: 1 })
    } else {
      if (!form.value.password || form.value.password.length < 8) {
        formError.value = 'Mật khẩu tối thiểu 8 ký tự'
        return
      }
      await authApi.register({
        name: form.value.name,
        username: form.value.username,
        email: form.value.email,
        password: form.value.password,
      })
      layui.layer.msg('Tạo tài khoản thành công', { icon: 1 })
    }
    showModal.value = false
    await loadUsers()
  } catch (e) {
    const detail = e.response?.data?.detail
    if (Array.isArray(detail)) {
      formError.value = detail.map(d => d.msg).join('; ')
    } else {
      formError.value = detail || e.message || 'Lỗi không xác định'
    }
  }
}

function deleteUser(userData) {
  layui.use(['layer'], (layer) => {
    layer.confirm(
      'Xóa tài khoản <b>' + userData.username + '</b> (' + userData.name + ')?',
      { title: 'Xác nhận xóa', btn: ['Xóa', 'Hủy'] },
      async (index) => {
        layer.close(index)
        try {
          await usersApi.delete(userData.id)
          layer.msg('Đã xóa thành công', { icon: 1 })
          await loadUsers()
        } catch (e) {
          layer.msg('Xóa thất bại: ' + (e.response?.data?.detail || e.message), { icon: 2 })
        }
      }
    )
  })
}

function toggleActive(userData) {
  const newStatus = !userData.is_active
  layui.use(['layer'], (layer) => {
    const action = newStatus ? 'Kích hoạt' : 'Khóa'
    layer.confirm(
      action + ' tài khoản <b>' + userData.username + '</b>?',
      { title: 'Xác nhận', btn: [action, 'Hủy'] },
      async (index) => {
        layer.close(index)
        try {
          await usersApi.update(userData.id, { is_active: newStatus })
          layer.msg(action + ' thành công', { icon: 1 })
          await loadUsers()
        } catch (e) {
          layer.msg('Thất bại: ' + (e.response?.data?.detail || e.message), { icon: 2 })
        }
      }
    )
  })
}

/* ===== RENDER TABLE ===== */
onMounted(() => {
  createTemplate('accountToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="add" title="Thêm tài khoản"><i class="layui-icon layui-icon-add-1"></i> Thêm tài khoản</button>
      <button class="layui-btn layui-btn-xs layui-btn-primary" lay-event="refresh" title="Làm mới"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)
  createTemplate('accountRowBar', `
    <div class="layui-btn-container">
      <a class="layui-btn layui-btn-xs layui-btn-warm" lay-event="edit" title="Sửa"><i class="layui-icon layui-icon-edit"></i></a>
      <a class="layui-btn layui-btn-xs layui-btn-normal" lay-event="toggle" title="Khóa/Mở khóa"><i class="layui-icon layui-icon-password"></i></a>
      <a class="layui-btn layui-btn-xs layui-btn-danger" lay-event="del" title="Xóa"><i class="layui-icon layui-icon-delete"></i></a>
    </div>
  `)

  nextTick(() => {
    layui.use(['table'], (table) => {
      tableIns = renderTable(table, {
        elem: '#accountTable',
        id: 'accountTable',
        escape: false,
        cols: [[
          { type: 'numbers', title: 'STT', width: 60 },
          { field: 'name', title: 'Tên', minWidth: 130 },
          { field: 'username', title: 'Username', width: 140 },
          { field: 'email', title: 'Email', minWidth: 180 },
          {
            field: 'is_superuser', title: 'Vai trò', width: 120,
            templet: (d) => {
              if (d.is_superuser) return '<span class="role-badge role-adminhub">ADMIN</span>'
              return '<span class="role-badge role-userhub">USER</span>'
            }
          },
          {
            field: 'is_active', title: 'Trạng thái', width: 110,
            templet: (d) => d.is_active
              ? '<span class="status-active">Hoạt động</span>'
              : '<span class="status-inactive">Khóa</span>'
          },
          {
            field: 'created_at', title: 'Ngày tạo', width: 160,
            templet: (d) => {
              if (!d.created_at) return '-'
              const dt = new Date(d.created_at)
              const pad = (n) => String(n).padStart(2, '0')
              return pad(dt.getDate()) + '/' + pad(dt.getMonth() + 1) + '/' + dt.getFullYear() + ' ' + pad(dt.getHours()) + ':' + pad(dt.getMinutes())
            }
          },
          { title: 'Thao tác', width: 150, align: 'center', fixed: 'right', toolbar: '#accountRowBar' },
        ]],
        data: [],
        page: false,
        toolbar: '#accountToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: 'Chưa có dữ liệu' },
      })

      table.on('toolbar(accountTable)', (obj) => {
        if (obj.event === 'add') {
          openAdd()
        } else if (obj.event === 'refresh') {
          loadUsers()
        }
      })

      table.on('tool(accountTable)', (obj) => {
        if (obj.event === 'edit') {
          openEdit(obj.data)
        } else if (obj.event === 'toggle') {
          toggleActive(obj.data)
        } else if (obj.event === 'del') {
          deleteUser(obj.data)
        }
      })

      loadUsers()
    })
  })
})

onUnmounted(() => {
  const oldView = document.querySelector('.layui-table-view[lay-id="accountTable"]')
  if (oldView) oldView.remove()
})
</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-group"></i> Quản lý tài khoản & Phân quyền
      </h3>
    </div>

    <table id="accountTable" lay-filter="accountTable"></table>
  </div>

  <Teleport to="body">
    <div v-if="showModal" class="acct-modal-overlay" @click.self="showModal = false">
      <div class="acct-modal">
        <div class="acct-modal-header">
          <h4>{{ editingUser ? 'Sửa tài khoản' : 'Thêm tài khoản mới' }}</h4>
          <i class="layui-icon layui-icon-close acct-modal-close" @click="showModal = false"></i>
        </div>
        <div class="acct-modal-body">
          <div v-if="formError" class="acct-form-error">
            <i class="layui-icon layui-icon-close-fill"></i> {{ formError }}
          </div>
          <div class="acct-form-field">
            <label>Họ tên</label>
            <input v-model="form.name" type="text" class="layui-input" placeholder="VD: Nguyễn Văn A" />
          </div>
          <div class="acct-form-field">
            <label>Username</label>
            <input v-model="form.username" type="text" class="layui-input" placeholder="VD: nguyenvana" :disabled="!!editingUser" />
          </div>
          <div class="acct-form-field">
            <label>Email</label>
            <input v-model="form.email" type="email" class="layui-input" placeholder="VD: user@example.com" />
          </div>
          <div class="acct-form-field">
            <label>Mật khẩu {{ editingUser ? '(để trống nếu không đổi)' : '(tối thiểu 8 ký tự)' }}</label>
            <input v-model="form.password" type="password" class="layui-input" placeholder="Nhập mật khẩu" />
          </div>
        </div>
        <div class="acct-modal-footer">
          <button class="layui-btn layui-btn-sm layui-btn-primary" @click="showModal = false">Hủy</button>
          <button class="layui-btn layui-btn-sm layui-btn-normal" @click="saveUser">
            <i class="layui-icon layui-icon-ok"></i> {{ editingUser ? 'Cập nhật' : 'Tạo mới' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.acct-modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.35); z-index: 19999; display: flex; align-items: center; justify-content: center; }
.acct-modal { background: #fff; border-radius: 6px; width: 380px; max-width: 92vw; box-shadow: 0 6px 24px rgba(0,0,0,0.18); }
.acct-modal-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid #e6e2da; }
.acct-modal-header h4 { margin: 0; font-size: 14px; font-weight: 700; color: #2e2a25; }
.acct-modal-close { font-size: 16px; color: #999; cursor: pointer; transition: color 0.15s; }
.acct-modal-close:hover { color: #e74c3c; }
.acct-modal-body { padding: 14px 16px; display: flex; flex-direction: column; gap: 12px; }
.acct-form-error { display: flex; align-items: center; gap: 6px; background: rgba(231,76,60,0.06); border: 1px solid rgba(231,76,60,0.15); border-radius: 4px; color: #c0392b; padding: 7px 10px; font-size: 12px; }
.acct-form-error .layui-icon { font-size: 13px; }
.acct-form-field { display: flex; flex-direction: column; gap: 4px; }
.acct-form-field label { font-size: 12px; color: #666; font-weight: 600; }
.acct-form-field .layui-input { height: 32px; font-size: 13px; border-color: #e6e2da; }
.acct-form-field .layui-input:focus { border-color: #16baaa; }
.acct-form-field .layui-input:disabled { background: #f5f5f5; color: #999; }
.acct-modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 10px 16px; border-top: 1px solid #e6e2da; }
</style>
