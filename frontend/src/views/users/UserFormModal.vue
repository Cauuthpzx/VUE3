<script setup>
import { ref, watch } from 'vue'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()

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
    error.value = t('users.nameRequired')
    return
  }
  if (!form.value.username.trim()) {
    error.value = t('users.usernameRequired')
    return
  }
  if (!form.value.email.trim()) {
    error.value = t('users.emailRequired')
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
      <h3>{{ t('users.editUser') }}</h3>

      <div v-if="error" class="user-modal-error">{{ error }}</div>

      <div class="layui-form-item">
        <label class="user-modal-label">{{ t('users.name') }}</label>
        <input v-model="form.name" type="text" class="layui-input" :placeholder="t('users.namePlaceholder')" />
      </div>

      <div class="layui-form-item">
        <label class="user-modal-label">{{ t('users.username') }}</label>
        <input v-model="form.username" type="text" class="layui-input" :placeholder="t('users.usernamePlaceholder')" />
      </div>

      <div class="layui-form-item">
        <label class="user-modal-label">{{ t('users.email') }}</label>
        <input v-model="form.email" type="text" class="layui-input" :placeholder="t('users.emailPlaceholder')" />
      </div>

      <div class="user-modal-actions">
        <button class="layui-btn layui-btn-sm" @click="handleSubmit">{{ t('common.save') }}</button>
        <button class="layui-btn layui-btn-sm layui-btn-primary" @click="$emit('close')">{{ t('common.cancel') }}</button>
      </div>
    </div>
  </div>
</template>
