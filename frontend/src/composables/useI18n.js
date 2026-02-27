import { computed } from 'vue'
import { defineStore, storeToRefs } from 'pinia'
import { ref } from 'vue'

import viMessages from '@/locales/vi.json'
import enMessages from '@/locales/en.json'
import zhCNMessages from '@/locales/zh-CN.json'

const allMessages = {
  vi: viMessages,
  en: enMessages,
  'zh-CN': zhCNMessages,
}

export const useLocaleStore = defineStore('locale', () => {
  const locale = ref(localStorage.getItem('lang') || 'vi')

  function setLocale(code) {
    locale.value = code
    localStorage.setItem('lang', code)
    document.documentElement.lang = code
  }

  return { locale, setLocale }
})

/**
 * Resolve nested key like "nav.home" from messages object
 */
function resolve(obj, key) {
  return key.split('.').reduce((o, k) => (o && o[k] !== undefined ? o[k] : null), obj)
}

/**
 * useI18n composable — provides reactive t() function
 * Usage: const { t, locale } = useI18n()
 */
export function useI18n() {
  const store = useLocaleStore()
  const { locale } = storeToRefs(store)

  const messages = computed(() => allMessages[locale.value] || allMessages.vi)

  function t(key, params) {
    let val = resolve(messages.value, key)
    if (val === null || val === undefined) {
      // fallback to Vietnamese
      val = resolve(allMessages.vi, key)
    }
    if (val === null || val === undefined) return key

    // Simple interpolation: {name} → params.name
    if (params && typeof val === 'string') {
      return val.replace(/\{(\w+)\}/g, (_, k) => (params[k] !== undefined ? params[k] : `{${k}}`))
    }
    return val
  }

  return { t, locale, setLocale: store.setLocale }
}
