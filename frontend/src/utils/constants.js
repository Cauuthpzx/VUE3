export const STORAGE_KEYS = {
  USER: 'user',
  SAVED_USERNAME: 'saved_username',
}

export const ERROR_MESSAGES = {
  LOGIN_FAILED: 'Login failed.',
  REGISTER_FAILED: 'Registration failed.',
  GENERIC: 'An error occurred.',
}

export const NUM_LOCALE = { vi: 'vi-VN', en: 'en-US', 'zh-CN': 'zh-CN' }

/**
 * Escape HTML special characters to prevent XSS when injecting into innerHTML/templates.
 */
export function escapeHtml(str) {
  if (str == null) return ''
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

/**
 * Format number with locale-aware separators.
 */
export function formatNumber(val, locale) {
  if (val == null || val === '') return '0'
  var num = parseFloat(val)
  if (isNaN(num)) return val
  return num.toLocaleString(NUM_LOCALE[locale] || 'vi-VN', { minimumFractionDigits: 0, maximumFractionDigits: 4 })
}
