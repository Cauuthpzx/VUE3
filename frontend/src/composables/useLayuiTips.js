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

/* ===== Shared close helper ===== */
let activeTipsIndex = null

function closeTips() {
  if (activeTipsIndex != null) {
    try { layui.layer.close(activeTipsIndex) } catch (_) { /* ignore */ }
    activeTipsIndex = null
  }
}

function showTips(content, el, direction, color) {
  closeTips()
  try {
    activeTipsIndex = layui.layer.tips(content, el, {
      tips: [direction || 1, color || TIPS_COLOR],
      time: 0,
      tipsMore: false,
    })
  } catch (_) { /* ignore if layer not ready */ }
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

  el._tipsEnter = () => showTips(content, el, direction, color)
  el._tipsLeave = () => closeTips()

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
  var checkTimer = null

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
    if (checkTimer) { clearInterval(checkTimer); checkTimer = null }
    if (currentEl) { restoreTitle(currentEl); currentEl = null }
    closeTips()
  }

  function startHoverCheck() {
    if (checkTimer) clearInterval(checkTimer)
    checkTimer = setInterval(function () {
      if (!currentEl) { clearInterval(checkTimer); checkTimer = null; return }
      if (!document.body.contains(currentEl) || !currentEl.matches(':hover')) {
        cleanup()
      }
    }, 150)
  }

  document.addEventListener('mouseover', function (e) {
    var el = findTipTarget(e.target)
    if (el && el === currentEl) return
    if (!el) {
      if (currentEl) cleanup()
      return
    }
    // New tip target
    if (currentEl) { restoreTitle(currentEl); closeTips() }
    currentEl = el
    var content = el.getAttribute('title')
    el._savedTitle = content
    el.removeAttribute('title')
    showTips(content, el, 1, TIPS_COLOR)
    startHoverCheck()
  }, true)

  document.addEventListener('mouseout', function (e) {
    if (!currentEl) return
    var related = e.relatedTarget
    if (!related || (!currentEl.contains(related) && related !== currentEl)) {
      cleanup()
    }
  }, true)

  document.addEventListener('click', function () { cleanup() }, true)
}
