/**
 * useLayuiLocale — Patch Layui built-in Chinese text (laypage, laydate)
 * to support the app's i18n system.
 *
 * Layui 2.13.3 hardcodes Chinese text for pagination and date picker.
 * This module uses MutationObserver to translate DOM text after Layui renders.
 *
 * Call initLayuiLocale() once after app.mount().
 */
import { useI18n } from '@/composables/useI18n'

/**
 * Translate laypage pagination text inside a container element.
 */
function patchLaypage(container, t) {
  // "共 X 条" → localized count
  var countEls = container.querySelectorAll('.layui-laypage-count')
  countEls.forEach(function (el) {
    var match = el.textContent.match(/\d+/)
    if (match) {
      el.textContent = t('layui.pageCount', { count: match[0] })
    }
  })

  // "条/页" text in limit select wrapper
  var limitEls = container.querySelectorAll('.layui-laypage-limits')
  limitEls.forEach(function (el) {
    // The text node after the <select> contains "条/页"
    el.childNodes.forEach(function (node) {
      if (node.nodeType === 3 && node.textContent.trim()) {
        node.textContent = ' ' + t('layui.pagePerPage') + ' '
      }
    })
  })

  // "到第" ... "页" ... "确定" in skip section
  var skipEls = container.querySelectorAll('.layui-laypage-skip')
  skipEls.forEach(function (el) {
    // Replace text nodes (到第, 页)
    el.childNodes.forEach(function (node) {
      if (node.nodeType === 3) {
        var txt = node.textContent.trim()
        if (txt === '到第') node.textContent = t('layui.pageGoTo') + ' '
        else if (txt === '页') node.textContent = ' '
      }
    })
    // "确定" button
    var btn = el.querySelector('.layui-laypage-btn')
    if (btn && (btn.textContent.trim() === '确定' || btn.textContent.trim())) {
      btn.textContent = t('layui.pageGo')
    }
  })
}

/**
 * Translate laydate popup text.
 */
function patchLaydate(container, t) {
  // Footer buttons: 清空, 现在, 确定
  var footerBtns = container.querySelectorAll('.laydate-footer-btns span, .layui-laydate-footer span')
  footerBtns.forEach(function (btn) {
    var txt = btn.textContent.trim()
    if (txt === '清空') btn.textContent = t('layui.dateClear')
    else if (txt === '现在') btn.textContent = t('layui.dateNow')
    else if (txt === '确定') btn.textContent = t('layui.dateConfirm')
  })
}

/**
 * Initialize MutationObserver to auto-patch Layui elements.
 * Call once after app.mount().
 */
export function initLayuiLocale() {
  var { t } = useI18n()

  // Patch existing elements on page
  function patchAll() {
    document.querySelectorAll('.layui-laypage').forEach(function (el) {
      patchLaypage(el, t)
    })
    document.querySelectorAll('.layui-laydate').forEach(function (el) {
      patchLaydate(el, t)
    })
  }

  // Observe DOM for new layui elements
  var observer = new MutationObserver(function (mutations) {
    var needPatch = false
    for (var i = 0; i < mutations.length; i++) {
      var added = mutations[i].addedNodes
      for (var j = 0; j < added.length; j++) {
        var node = added[j]
        if (node.nodeType !== 1) continue
        if (
          node.classList.contains('layui-laypage') ||
          node.classList.contains('layui-laydate') ||
          node.querySelector('.layui-laypage') ||
          node.querySelector('.layui-laydate')
        ) {
          needPatch = true
          break
        }
      }
      if (needPatch) break
    }
    if (needPatch) patchAll()
  })

  observer.observe(document.body, { childList: true, subtree: true })

  // Also patch after a short delay for initial render
  setTimeout(patchAll, 500)
}
