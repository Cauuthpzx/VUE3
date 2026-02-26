import { onUnmounted } from 'vue'

/**
 * Composable để tạo và quản lý <script type="text/html"> templates cho layui.
 * Auto-cleanup tất cả templates khi component unmount.
 */
export function useLayuiTemplate() {
  const templateIds = []

  function createTemplate(id, html) {
    let el = document.getElementById(id)
    if (el) el.remove()
    el = document.createElement('script')
    el.type = 'text/html'
    el.id = id
    el.innerHTML = html
    document.body.appendChild(el)

    if (!templateIds.includes(id)) {
      templateIds.push(id)
    }
  }

  function removeTemplate(id) {
    const el = document.getElementById(id)
    if (el) el.remove()
    const idx = templateIds.indexOf(id)
    if (idx !== -1) templateIds.splice(idx, 1)
  }

  onUnmounted(() => {
    templateIds.forEach((id) => {
      const el = document.getElementById(id)
      if (el) el.remove()
    })
  })

  return { createTemplate, removeTemplate }
}
