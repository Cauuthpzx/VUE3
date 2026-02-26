<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { usersApi } from '@/api/users'
import { ERROR_MESSAGES } from '@/utils/constants'
import UserFormModal from './UserFormModal.vue'

const users = ref([])
const total = ref(0)
const page = ref(1)
const limit = ref(20)
const search = ref('')
const loading = ref(false)

const showModal = ref(false)
const editingUser = ref(null)

onMounted(() => {
  loadUsers()
})

async function loadUsers() {
  loading.value = true
  try {
    const { data } = await usersApi.list({
      skip: (page.value - 1) * limit.value,
      limit: limit.value,
    })
    users.value = data
    total.value = data.length
    await nextTick()
    renderPagination()
  } finally {
    loading.value = false
  }
}

function renderPagination() {
  layui.use(['laypage'], () => {
    layui.laypage.render({
      elem: 'users-pagination',
      count: total.value,
      limit: limit.value,
      curr: page.value,
      layout: ['count', 'prev', 'page', 'next'],
      jump(obj, first) {
        if (!first) {
          page.value = obj.curr
          loadUsers()
        }
      },
    })
  })
}

function handleSearch() {
  page.value = 1
  loadUsers()
}

function filteredUsers() {
  if (!search.value.trim()) return users.value
  const q = search.value.toLowerCase()
  return users.value.filter(
    (u) =>
      u.name.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q) ||
      u.username.toLowerCase().includes(q),
  )
}

function openEdit(user) {
  editingUser.value = { ...user }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingUser.value = null
}

async function handleSave(formData) {
  try {
    await usersApi.update(editingUser.value.id, formData)
    layui.layer.msg('Cập nhật thành công', { icon: 1, time: 1500 })
    closeModal()
    await loadUsers()
  } catch (err) {
    const msg = err.response?.data?.detail || ERROR_MESSAGES.GENERIC
    layui.layer.msg(msg, { icon: 2, time: 2000 })
  }
}

function confirmDelete(user) {
  layui.layer.confirm(
    `Xóa người dùng <b>${user.name}</b>?`,
    { title: 'Xác nhận xóa', btn: ['Xóa', 'Hủy'] },
    async (index) => {
      try {
        await usersApi.delete(user.id)
        layui.layer.msg('Đã xóa', { icon: 1, time: 1500 })
        layui.layer.close(index)
        await loadUsers()
      } catch (err) {
        const msg = err.response?.data?.detail || ERROR_MESSAGES.GENERIC
        layui.layer.msg(msg, { icon: 2, time: 2000 })
      }
    },
  )
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>

<template>
  <div class="users-page">
    <!-- Toolbar -->
    <div class="users-toolbar">
      <div class="users-toolbar-left">
        <div class="layui-input-inline" style="width: 260px;">
          <input
            v-model="search"
            type="text"
            placeholder="Tìm theo tên, username, email..."
            class="layui-input layui-input-sm"
            @keyup.enter="handleSearch"
          />
        </div>
        <button class="layui-btn layui-btn-sm layui-btn-primary" @click="handleSearch">
          <i class="layui-icon layui-icon-search"></i>
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="layui-card">
      <div class="layui-card-body" style="padding: 0;">
        <table class="layui-table users-table">
          <colgroup>
            <col width="50" />
            <col />
            <col width="140" />
            <col width="220" />
            <col width="90" />
            <col width="110" />
            <col width="130" />
          </colgroup>
          <thead>
            <tr>
              <th>#</th>
              <th>Tên</th>
              <th>Username</th>
              <th>Email</th>
              <th>Trạng thái</th>
              <th>Ngày tạo</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in filteredUsers()" :key="user.id">
              <td>{{ (page - 1) * limit + index + 1 }}</td>
              <td>{{ user.name }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
              <td>
                <span :class="user.is_active ? 'users-status-active' : 'users-status-inactive'">
                  {{ user.is_active ? 'Hoạt động' : 'Bị khóa' }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <button class="layui-btn layui-btn-xs" @click="openEdit(user)">Sửa</button>
                <button class="layui-btn layui-btn-xs layui-btn-danger" @click="confirmDelete(user)">Xóa</button>
              </td>
            </tr>
            <tr v-if="filteredUsers().length === 0 && !loading">
              <td colspan="7" style="text-align: center; color: #999;">Không có dữ liệu</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div id="users-pagination" class="users-pagination"></div>

    <!-- Edit Modal -->
    <UserFormModal
      v-if="showModal"
      :user="editingUser"
      @close="closeModal"
      @save="handleSave"
    />
  </div>
</template>
