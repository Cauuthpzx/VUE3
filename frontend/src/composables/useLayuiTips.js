/**
 * useLayuiTips — Vue directive cho layui layer.tips
 *
 * Sử dụng:
 *   v-tips="'Nội dung tooltip'"
 *   v-tips="{ content: 'Nội dung', direction: 1, color: '#16baaa' }"
 *
 * direction: 1=top, 2=right, 3=bottom, 4=left (mặc định: 1)
 */

let tipsIndex = null

export const vTips = {
  mounted(el, binding) {
    const val = binding.value
    if (!val) return

    const isObj = typeof val === 'object'
    const content = isObj ? val.content : val
    const direction = isObj && val.direction ? val.direction : 1
    const color = isObj && val.color ? val.color : '#2e2a25'
    const time = isObj && val.time != null ? val.time : 0

    if (!content) return

    // Xóa native title để tránh trùng
    el.removeAttribute('title')

    el._tipsEnter = () => {
      layui.use('layer', (layer) => {
        // Đóng tips cũ
        if (tipsIndex != null) {
          layer.close(tipsIndex)
        }
        tipsIndex = layer.tips(content, el, {
          tips: [direction, color],
          time,
          tipsMore: false,
        })
      })
    }

    el._tipsLeave = () => {
      if (tipsIndex != null) {
        layui.use('layer', (layer) => {
          layer.close(tipsIndex)
          tipsIndex = null
        })
      }
    }

    el.addEventListener('mouseenter', el._tipsEnter)
    el.addEventListener('mouseleave', el._tipsLeave)
  },

  updated(el, binding) {
    // Cập nhật content khi binding thay đổi
    const val = binding.value
    const isObj = typeof val === 'object'
    const content = isObj ? val.content : val

    // Xóa native title
    el.removeAttribute('title')

    // Re-bind handlers
    if (el._tipsEnter) {
      el.removeEventListener('mouseenter', el._tipsEnter)
      el.removeEventListener('mouseleave', el._tipsLeave)
    }

    if (!content) return

    const direction = isObj && val.direction ? val.direction : 1
    const color = isObj && val.color ? val.color : '#2e2a25'
    const time = isObj && val.time != null ? val.time : 0

    el._tipsEnter = () => {
      layui.use('layer', (layer) => {
        if (tipsIndex != null) layer.close(tipsIndex)
        tipsIndex = layer.tips(content, el, {
          tips: [direction, color],
          time,
          tipsMore: false,
        })
      })
    }

    el._tipsLeave = () => {
      if (tipsIndex != null) {
        layui.use('layer', (layer) => {
          layer.close(tipsIndex)
          tipsIndex = null
        })
      }
    }

    el.addEventListener('mouseenter', el._tipsEnter)
    el.addEventListener('mouseleave', el._tipsLeave)
  },

  unmounted(el) {
    if (el._tipsEnter) {
      el.removeEventListener('mouseenter', el._tipsEnter)
      el.removeEventListener('mouseleave', el._tipsLeave)
    }
    if (tipsIndex != null) {
      layui.use('layer', (layer) => {
        layer.close(tipsIndex)
        tipsIndex = null
      })
    }
  },
}
