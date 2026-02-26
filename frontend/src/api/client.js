import axios from 'axios'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`
  }
  return config
})

let isRefreshing = false
let failedQueue = []

function processQueue(error, token = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  failedQueue = []
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return client(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const authStore = useAuthStore()
      try {
        const success = await authStore.refreshToken()
        if (success) {
          const newToken = authStore.accessToken
          processQueue(null, newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return client(originalRequest)
        }
      } catch (refreshError) {
        processQueue(refreshError, null)
      } finally {
        isRefreshing = false
      }

      authStore.clearAuth()
      router.push({ name: 'login' })
    }

    return Promise.reject(error)
  }
)

export function createCancelToken() {
  const controller = new AbortController()
  return {
    signal: controller.signal,
    cancel: () => controller.abort(),
  }
}

export default client
