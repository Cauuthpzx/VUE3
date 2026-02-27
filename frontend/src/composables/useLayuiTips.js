/**
 * useLayuiTips — Vue directive + Global auto-tips for layui layer.tips
 *
 * 1) v-tips directive (Vue template elements):
 *    v-tips="'Tooltip text'"
 *    v-tips="{ content: 'Text', direction: 1, color: '#16baaa' }"
 *
 * 2) initGlobalTips() — auto-converts native [title] on .layui-btn
 *    into layer.tips() via event delegation. Call once after app.mount().
 *
 * direction: 1=top, 2=right, 3=bottom, 4=left (default: 1)
 */

const TIPS_COLOR = '#2e2a25'

/* ===== Shared close/show using pure layui API ===== */
let activeTipsIndex = null

function closeTips() {
  if (activeTipsIndex != null) {
    layui.layer.close(activeTipsIndex)
    activeTipsIndex = null
  }
}

function showTips(content, el, direction, color) {
  closeTips()
  activeTipsIndex = layui.layer.tips(content, el, {
    tips: [direction || 1, color || TIPS_COLOR],
    time: 0,
    tipsMore: false,
  })
}

/* ===== vTips directive (for Vue template elements) ===== */
function bindTips(el, binding) {
  const val = binding.value
  if (el._tipsEnter) {
    el.removeEventListener('mouseenter', el._tipsEnter)
    el.removeEventListener('mouseleave', el._tipsLeave)
  }

  const isObj = typeof val === 'object' && val !== null
  const content = isObj ? val.content : val
  if (!content) return

  const direction = isObj && val.direction ? val.direction : 1
  const color = isObj && val.color ? val.color : TIPS_COLOR

  el.removeAttribute('title')
  el._tipsManaged = true

  el._tipsEnter = function () { showTips(content, el, direction, color) }
  el._tipsLeave = function () { closeTips() }

  el.addEventListener('mouseenter', el._tipsEnter)
  el.addEventListener('mouseleave', el._tipsLeave)
}

export const vTips = {
  mounted(el, binding) {
    bindTips(el, binding)
  },
  updated(el, binding) {
    bindTips(el, binding)
  },
  unmounted(el) {
    if (el._tipsEnter) {
      el.removeEventListener('mouseenter', el._tipsEnter)
      el.removeEventListener('mouseleave', el._tipsLeave)
    }
    closeTips()
  },
}

/* ===== Global auto-tips (for layui-rendered elements with [title]) ===== */
/**
 * Call once after app.mount(). Uses event delegation so it works for
 * dynamically rendered layui table toolbar/row buttons.
 */
export function initGlobalTips() {
  var currentEl = null

  function findTipTarget(target) {
    if (!target || !target.closest) return null
    var el = target.closest('[title]')
    if (!el || !el.getAttribute('title')) return null
    if (el._tipsManaged) return null
    if (
      el.classList.contains('layui-btn') ||
      el.classList.contains('layui-btn-disabled') ||
      el.hasAttribute('lay-event') ||
      el.closest('.app-notify-bell') ||
      el.classList.contains('acct-modal-close')
    ) {
      return el
    }
    return null
  }

  function restoreTitle(el) {
    if (el && el._savedTitle) {
      el.setAttribute('title', el._savedTitle)
      delete el._savedTitle
    }
  }

  function cleanup() {
    if (currentEl) { restoreTitle(currentEl); currentEl = null }
    closeTips()
  }

  document.addEventListener('mouseenter', function (e) {
    var el = findTipTarget(e.target)
    if (!el) return
    if (el === currentEl) return
    // Switch to new target
    if (currentEl) { restoreTitle(currentEl) }
    currentEl = el
    var content = el.getAttribute('title')
    el._savedTitle = content
    el.removeAttribute('title')
    showTips(content, el, 1, TIPS_COLOR)
  }, true)

  document.addEventListener('mouseleave', function (e) {
    if (!currentEl) return
    if (e.target === currentEl || currentEl.contains(e.target)) {
      var related = e.relatedTarget
      if (!related || !currentEl.contains(related)) {
        cleanup()
      }
    }
  }, true)

  document.addEventListener('click', function () { cleanup() }, true)
}
