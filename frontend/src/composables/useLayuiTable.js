import { onUnmounted } from 'vue'
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
 * Usage:
 *   const { renderTable } = useLayuiTable()
 *   renderTable(table, { elem: '#myTable', id: 'myTable', ... })
 */
export function useLayuiTable() {
  const tableIds = []
  const authStore = useAuthStore()
  const { t } = useI18n()

  function cleanupTable(tableId) {
    // Remove layui-generated table-view container
    const views = document.querySelectorAll(`.layui-table-view[lay-id="${tableId}"]`)
    views.forEach((el) => el.remove())
  }

  function renderTable(table, config) {
    const id = config.id || config.elem?.replace('#', '')
    if (id) {
      cleanupTable(id)
      if (!tableIds.includes(id)) {
        tableIds.push(id)
      }
    }

    // Translate defaultToolbar built-in buttons
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

    // Inject dynamic auth header via `before` callback — always uses fresh token
    if (config.url) {
      const userBefore = config.before
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

  onUnmounted(() => {
    tableIds.forEach((id) => {
      cleanupTable(id)
    })
  })

  return { renderTable, cleanupTable }
}
