import { onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'

/**
 * Composable to manage layui table lifecycle — prevents duplicate table views
 * when Vue components re-mount (navigate away then back).
 *
 * Automatically injects current auth token via `before` callback so that
 * token refresh is picked up on every request (pagination, reload, etc.).
 *
 * Automatically translates defaultToolbar built-in buttons (filter, exports, print).
 *
 * onLocaleChange(fn) — registers a callback that fires when locale changes.
 * Use this to re-init tables with fresh translations.
 *
 * Usage:
 *   const { renderTable, onLocaleChange } = useLayuiTable()
 *   function initTable() { createTemplate(...); renderTable(table, {...}) }
 *   onLocaleChange(initTable)
 */
export function useLayuiTable() {
  const tableIds = []
  const authStore = useAuthStore()
  const { t, locale } = useI18n()
  const localeCallbacks = []

  function cleanupTable(tableId) {
    var views = document.querySelectorAll('.layui-table-view[lay-id="' + tableId + '"]')
    views.forEach(function (el) { el.remove() })
  }

  function translateToolbar(config) {
    if (Array.isArray(config.defaultToolbar)) {
      var toolbarMap = {
        filter: { title: t('table.filter'), layEvent: 'LAYTABLE_COLS', icon: 'layui-icon-cols' },
        exports: { title: t('table.exports'), layEvent: 'LAYTABLE_EXPORT', icon: 'layui-icon-export' },
        print: { title: t('table.print'), layEvent: 'LAYTABLE_PRINT', icon: 'layui-icon-print' },
      }
      config.defaultToolbar = config.defaultToolbar.map(function (item) {
        if (typeof item === 'string' && toolbarMap[item]) return toolbarMap[item]
        return item
      })
    }
  }

  function renderTable(table, config) {
    var id = config.id || (config.elem ? config.elem.replace('#', '') : '')
    if (id) {
      cleanupTable(id)
      if (!tableIds.includes(id)) {
        tableIds.push(id)
      }
    }

    translateToolbar(config)

    // Inject dynamic auth header via `before` callback — always uses fresh token
    if (config.url) {
      var userBefore = config.before
      config.before = function (options) {
        if (authStore.accessToken) {
          options.headers = options.headers || {}
          options.headers.Authorization = 'Bearer ' + authStore.accessToken
        }
        if (userBefore) userBefore.call(this, options)
      }
    }

    return table.render(config)
  }

  /**
   * Reload an existing table with updated config (cols, toolbar, text, etc.)
   * without destroying it. Preserves current pagination state (page, where).
   * Use this in onLocaleChange for paginated tables.
   */
  function reloadTable(table, id, config) {
    translateToolbar(config)
    table.reload(id, config)
  }

  /**
   * Register a callback to re-init table when locale changes.
   * The callback should recreate templates + re-render the table.
   */
  function onLocaleChange(fn) {
    localeCallbacks.push(fn)
  }

  // Watch locale — re-run all registered callbacks
  watch(locale, function () {
    localeCallbacks.forEach(function (fn) { fn() })
  })

  onUnmounted(function () {
    tableIds.forEach(function (id) {
      cleanupTable(id)
    })
    localeCallbacks.length = 0
  })

  return { renderTable, reloadTable, cleanupTable, onLocaleChange }
}
