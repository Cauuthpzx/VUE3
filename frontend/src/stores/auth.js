import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const userName = computed(() => user.value?.name || '')

  async function login(credentials) {
    const { data } = await authApi.login(credentials)
    accessToken.value = data.access_token
    await fetchUser()
  }

  async function register(formData) {
    await authApi.register(formData)
  }

  async function fetchUser() {
    const { data } = await authApi.me()
    user.value = data
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clearAuth()
    }
  }

  async function refreshToken() {
    try {
      const { data } = await authApi.refresh()
      accessToken.value = data.access_token
    } catch {
      clearAuth()
    }
  }

  function clearAuth() {
    accessToken.value = null
    user.value = null
  }

  return {
    accessToken,
    user,
    isAuthenticated,
    userName,
    login,
    register,
    fetchUser,
    logout,
    refreshToken,
    clearAuth,
  }
})
