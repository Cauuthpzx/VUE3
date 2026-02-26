<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SvgIcon from '@/components/SvgIcon.vue'
import { STORAGE_KEYS, ERROR_MESSAGES } from '@/utils/constants'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: '',
})
const rememberMe = ref(false)
const loading = ref(false)
const errorMsg = ref('')
const showPassword = ref(false)

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEYS.SAVED_USERNAME)
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      form.value.username = parsed.username || ''
      rememberMe.value = true
    } catch { /* ignore */ }
  }

  layui.use(['form'], () => {
    const layForm = layui.form
    layForm.render()

    layForm.on('submit(loginSubmit)', () => {
      handleLogin()
      return false
    })
  })
})

async function handleLogin() {
  errorMsg.value = ''
  loading.value = true

  try {
    await authStore.login({
      username: form.value.username,
      password: form.value.password,
    })

    if (rememberMe.value) {
      localStorage.setItem(STORAGE_KEYS.SAVED_USERNAME, JSON.stringify({
        username: form.value.username,
      }))
    } else {
      localStorage.removeItem(STORAGE_KEYS.SAVED_USERNAME)
    }

    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || ERROR_MESSAGES.LOGIN_FAILED
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="auth-logo">
        <div class="auth-logo-circle">
          <SvgIcon name="sign-in" :size="26" />
        </div>
      </div>
      <h2>Đăng nhập</h2>
      <p class="subtitle">Chào mừng bạn quay lại</p>

      <form class="layui-form" lay-filter="loginForm">
        <div class="layui-form-item">
          <div class="input-icon-wrap">
            <SvgIcon name="account" :size="20" class="input-icon" />
            <input
              v-model="form.username"
              type="text"
              name="username"
              placeholder="Tên đăng nhập hoặc email"
              autocomplete="username"
              lay-verify="required"
              class="layui-input input-with-icon"
            />
          </div>
        </div>

        <div class="layui-form-item">
          <div class="input-icon-wrap">
            <SvgIcon name="lock" :size="20" class="input-icon" />
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              name="password"
              placeholder="Mật khẩu"
              autocomplete="current-password"
              lay-verify="required"
              class="layui-input input-with-icon input-with-eye"
            />
            <span class="input-eye" @click="showPassword = !showPassword">
              <SvgIcon :name="showPassword ? 'eye' : 'eye-closed'" :size="18" />
            </span>
          </div>
        </div>

        <div class="layui-form-item remember-row">
          <label class="remember-label" @click="rememberMe = !rememberMe">
            <span class="remember-check" :class="{ checked: rememberMe }">
              <SvgIcon v-if="rememberMe" name="check" :size="12" />
            </span>
            <span>Nhớ tên đăng nhập</span>
          </label>
        </div>

        <div v-if="errorMsg" class="layui-form-item">
          <div class="form-error-box">
            <SvgIcon name="error-small" :size="15" />
            <span>{{ errorMsg }}</span>
          </div>
        </div>

        <div class="layui-form-item" style="margin-top: 22px;">
          <button
            type="button"
            class="layui-btn layui-btn-normal layui-btn-fluid auth-submit-btn"
            lay-submit
            lay-filter="loginSubmit"
            :disabled="loading"
          >
            <SvgIcon v-if="!loading" name="sign-in" :size="18" style="margin-right: 6px;" />
            {{ loading ? 'Đang xử lý...' : 'Đăng nhập' }}
          </button>
        </div>
      </form>

      <div class="auth-divider">
        <span>hoặc</span>
      </div>

      <div class="auth-footer">
        Chưa có tài khoản?
        <router-link to="/register">
          <SvgIcon name="person-add" :size="15" style="margin-right: 2px;" />
          Đăng ký ngay
        </router-link>
      </div>
    </div>
  </div>
</template>
