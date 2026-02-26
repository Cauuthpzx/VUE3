import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { STORAGE_KEYS } from '@/utils/constants'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(null)
  const user = ref(JSON.parse(localStorage.getItem(STORAGE_KEYS.USER) || 'null'))
  let initPromise = null

  const isAuthenticated = computed(() => !!accessToken.value)
  const userName = computed(() => user.value?.name || '')

  function setToken(token) {
    accessToken.value = token
  }

  function setUser(data) {
    user.value = data
    if (data) {
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(data))
    } else {
      localStorage.removeItem(STORAGE_KEYS.USER)
    }
  }

  async function login(credentials) {
    const { data } = await authApi.login(credentials)
    setToken(data.access_token)
    await fetchUser()
  }

  async function register(formData) {
    await authApi.register(formData)
  }

  async function fetchUser() {
    const { data } = await authApi.me()
    setUser(data)
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
      setToken(data.access_token)
      return true
    } catch {
      clearAuth()
      return false
    }
  }

  async function init() {
    if (!initPromise) {
      initPromise = (async () => {
        if (user.value && !accessToken.value) {
          await refreshToken()
        }
      })()
    }
    return initPromise
  }

  function clearAuth() {
    setToken(null)
    setUser(null)
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
    init,
    clearAuth,
  }
})
