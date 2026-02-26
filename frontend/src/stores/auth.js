import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token'))
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!accessToken.value)
  const userName = computed(() => user.value?.name || '')

  function setToken(token) {
    accessToken.value = token
    if (token) {
      localStorage.setItem('access_token', token)
    } else {
      localStorage.removeItem('access_token')
    }
  }

  function setUser(data) {
    user.value = data
    if (data) {
      localStorage.setItem('user', JSON.stringify(data))
    } else {
      localStorage.removeItem('user')
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
    } catch {
      clearAuth()
    }
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
    clearAuth,
  }
})
