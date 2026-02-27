import { onUnmounted } from 'vue'

/**
 * Composable to manage layui table lifecycle — prevents duplicate table views
 * when Vue components re-mount (navigate away then back).
 *
 * Usage:
 *   const { renderTable } = useLayuiTable()
 *   renderTable(table, { elem: '#myTable', id: 'myTable', ... })
 */
export function useLayuiTable() {
  const tableIds = []

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
    return table.render(config)
  }

  onUnmounted(() => {
    tableIds.forEach((id) => {
      cleanupTable(id)
    })
  })

  return { renderTable, cleanupTable }
}
