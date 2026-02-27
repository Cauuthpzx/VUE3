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

/* ── Bright-red console warning when server is unreachable ── */
const _serverWarnStyle = 'color:#ff0000;font-size:14px;font-weight:bold;background:#fff0f0;padding:2px 6px;border:1px solid #ff0000;border-radius:3px'
const _serverWarnPrefix = '%c⚠ SERVER DISCONNECTED'

let _lastWarnTs = 0
function warnServerDown(detail) {
  const now = Date.now()
  // throttle: max 1 warning per 3 seconds to avoid console spam
  if (now - _lastWarnTs < 3000) return
  _lastWarnTs = now
  console.error(_serverWarnPrefix, _serverWarnStyle)
  console.error(
    '%c🔴 Không thể kết nối đến server! Chi tiết: %s',
    'color:#ff0000;font-size:12px;font-weight:bold',
    detail
  )
  console.error(
    '%c   URL: %s',
    'color:#ff0000;font-size:11px',
    import.meta.env.VITE_API_URL || '(not set)'
  )
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    /* ── Detect server disconnection ── */
    if (!error.response) {
      // No response at all → network error / server down / timeout
      if (error.code === 'ECONNABORTED') {
        warnServerDown('Request timeout — server không phản hồi')
      } else if (error.code === 'ERR_NETWORK') {
        warnServerDown('Network error — server đã ngắt kết nối hoặc không thể truy cập')
      } else if (error.code === 'ERR_CANCELED') {
        // Request was intentionally aborted — not a server issue, skip warning
      } else {
        warnServerDown(`${error.message || 'Unknown error'} (code: ${error.code || 'none'})`)
      }
    } else if (error.response.status >= 502 && error.response.status <= 504) {
      // 502 Bad Gateway / 503 Service Unavailable / 504 Gateway Timeout
      warnServerDown(`HTTP ${error.response.status} — server gặp sự cố (${error.response.statusText})`)
    }

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

export default client
