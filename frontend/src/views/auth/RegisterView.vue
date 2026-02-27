<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SvgIcon from '@/components/SvgIcon.vue'
import { ERROR_MESSAGES } from '@/utils/constants'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  name: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})
const loading = ref(false)
const errorMsg = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)

onMounted(() => {
  layui.use(['form'], () => {
    const layForm = layui.form

    layForm.verify({
      confirmPass(value) {
        if (value !== form.value.password) {
          return t('auth.confirmPassMismatch')
        }
      },
      username(value) {
        if (!/^[a-z0-9_]{2,30}$/.test(value)) {
          return t('auth.usernameRule')
        }
      },
      pass(value) {
        if (value.length < 8) {
          return t('auth.passwordMinRule')
        }
      },
    })

    layForm.render()

    layForm.on('submit(registerSubmit)', () => {
      handleRegister()
      return false
    })
  })
})

async function handleRegister() {
  errorMsg.value = ''
  loading.value = true

  try {
    await authStore.register({
      name: form.value.name,
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
    })

    layui.layer.msg(t('auth.registerSuccess'), { icon: 1 })

    await nextTick()
    router.push({ name: 'login' })
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || ERROR_MESSAGES.REGISTER_FAILED
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
          <SvgIcon name="person-add" :size="26" />
        </div>
      </div>
      <h2>{{ t('auth.register') }}</h2>
      <p class="subtitle">{{ t('auth.createAccount') }}</p>

      <form class="layui-form" lay-filter="registerForm">
        <div class="layui-form-item">
          <div class="input-icon-wrap">
            <SvgIcon name="person" :size="20" class="input-icon" />
            <input
              v-model="form.name"
              type="text"
              name="name"
              :placeholder="t('auth.fullName')"
              autocomplete="name"
              lay-verify="required"
              class="layui-input input-with-icon"
            />
          </div>
        </div>

        <div class="layui-form-item">
          <div class="input-icon-wrap">
            <SvgIcon name="account" :size="20" class="input-icon" />
            <input
              v-model="form.username"
              type="text"
              name="username"
              :placeholder="t('auth.usernameLower')"
              autocomplete="username"
              lay-verify="required|username"
              class="layui-input input-with-icon"
            />
          </div>
        </div>

        <div class="layui-form-item">
          <div class="input-icon-wrap">
            <SvgIcon name="mail" :size="20" class="input-icon" />
            <input
              v-model="form.email"
              type="email"
              name="email"
              placeholder="Email"
              autocomplete="email"
              lay-verify="required|email"
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
              :placeholder="t('auth.passwordMin8')"
              autocomplete="new-password"
              lay-verify="required|pass"
              class="layui-input input-with-icon input-with-eye"
            />
            <span class="input-eye" @click="showPassword = !showPassword">
              <SvgIcon :name="showPassword ? 'eye' : 'eye-closed'" :size="18" />
            </span>
          </div>
        </div>

        <div class="layui-form-item">
          <div class="input-icon-wrap">
            <SvgIcon name="shield" :size="20" class="input-icon" />
            <input
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              name="confirmPassword"
              :placeholder="t('auth.confirmPassword')"
              autocomplete="new-password"
              lay-verify="required|confirmPass"
              class="layui-input input-with-icon input-with-eye"
            />
            <span class="input-eye" @click="showConfirmPassword = !showConfirmPassword">
              <SvgIcon :name="showConfirmPassword ? 'eye' : 'eye-closed'" :size="18" />
            </span>
          </div>
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
            lay-filter="registerSubmit"
            :disabled="loading"
          >
            <SvgIcon v-if="!loading" name="person-add" :size="18" style="margin-right: 6px;" />
            {{ loading ? t('common.processing') : t('auth.register') }}
          </button>
        </div>
      </form>

      <div class="auth-divider">
        <span>{{ t('common.or') }}</span>
      </div>

      <div class="auth-footer">
        {{ t('auth.hasAccount') }}
        <router-link to="/login">
          <SvgIcon name="sign-in" :size="15" style="margin-right: 2px;" />
          {{ t('auth.login') }}
        </router-link>
      </div>
    </div>
  </div>
</template>
