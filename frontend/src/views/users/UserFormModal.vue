<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  user: { type: Object, default: null },
})

const emit = defineEmits(['close', 'save'])

const form = ref({
  name: '',
  username: '',
  email: '',
})

const error = ref('')

watch(
  () => props.user,
  (val) => {
    if (val) {
      form.value = {
        name: val.name || '',
        username: val.username || '',
        email: val.email || '',
      }
    }
  },
  { immediate: true },
)

function handleSubmit() {
  error.value = ''

  if (!form.value.name.trim()) {
    error.value = 'Vui lòng nhập tên'
    return
  }
  if (!form.value.username.trim()) {
    error.value = 'Vui lòng nhập username'
    return
  }
  if (!form.value.email.trim()) {
    error.value = 'Vui lòng nhập email'
    return
  }

  const data = {}
  if (form.value.name !== props.user.name) data.name = form.value.name
  if (form.value.username !== props.user.username) data.username = form.value.username
  if (form.value.email !== props.user.email) data.email = form.value.email

  if (Object.keys(data).length === 0) {
    emit('close')
    return
  }

  emit('save', data)
}

function handleOverlayClick(e) {
  if (e.target === e.currentTarget) {
    emit('close')
  }
}
</script>

<template>
  <div class="user-modal-overlay" @click="handleOverlayClick">
    <div class="user-modal">
      <h3>Chỉnh sửa người dùng</h3>

      <div v-if="error" class="user-modal-error">{{ error }}</div>

      <div class="layui-form-item">
        <label class="user-modal-label">Tên</label>
        <input v-model="form.name" type="text" class="layui-input" placeholder="Nhập tên" />
      </div>

      <div class="layui-form-item">
        <label class="user-modal-label">Username</label>
        <input v-model="form.username" type="text" class="layui-input" placeholder="Nhập username" />
      </div>

      <div class="layui-form-item">
        <label class="user-modal-label">Email</label>
        <input v-model="form.email" type="text" class="layui-input" placeholder="Nhập email" />
      </div>

      <div class="user-modal-actions">
        <button class="layui-btn layui-btn-sm" @click="handleSubmit">Lưu</button>
        <button class="layui-btn layui-btn-sm layui-btn-primary" @click="$emit('close')">Hủy</button>
      </div>
    </div>
  </div>
</template>
