/**
 * useLayuiLocale — Patch Layui built-in Chinese text (laypage, laydate)
 * to support the app's i18n system.
 *
 * Layui 2.13.3 hardcodes Chinese text for pagination and date picker.
 * This module uses MutationObserver to translate DOM text after Layui renders.
 *
 * Call initLayuiLocale() once after app.mount().
 */
import { watch } from 'vue'
import { useI18n } from '@/composables/useI18n'

/**
 * Translate laypage pagination text inside a container element.
 */
function patchLaypage(container, t) {
  var perPage = t('layui.pagePerPage')

  // "共 X 条" → localized count
  var countEls = container.querySelectorAll('.layui-laypage-count')
  countEls.forEach(function (el) {
    var match = el.textContent.match(/\d+/)
    if (match) {
      el.textContent = t('layui.pageCount', { count: match[0] })
    }
  })

  // Limits select: "10 条/页" → "10 /trang" inside <option> + text node
  var limitEls = container.querySelectorAll('.layui-laypage-limits')
  limitEls.forEach(function (el) {
    // Patch <option> text: "10 条/页" → "10 /trang"
    var options = el.querySelectorAll('select option')
    options.forEach(function (opt) {
      var num = opt.value || opt.textContent.match(/\d+/)
      if (num) {
        opt.textContent = num + ' ' + perPage
      }
    })
    // Patch text node after <select> (some layui versions put "条/页" outside)
    el.childNodes.forEach(function (node) {
      if (node.nodeType === 3 && node.textContent.trim()) {
        node.textContent = ' '
      }
    })
  })

  // "到第" [input] "页" [button确定] in skip section
  // After translation, text nodes could be any language — use position-based patching
  var skipEls = container.querySelectorAll('.layui-laypage-skip')
  skipEls.forEach(function (el) {
    var textNodes = []
    el.childNodes.forEach(function (node) {
      if (node.nodeType === 3) textNodes.push(node)
    })
    // First text node = "到第" label, rest = spacers
    if (textNodes.length > 0) {
      textNodes[0].textContent = t('layui.pageGoTo') + ' '
    }
    for (var i = 1; i < textNodes.length; i++) {
      textNodes[i].textContent = ' '
    }
    var btn = el.querySelector('.layui-laypage-btn')
    if (btn) {
      btn.textContent = t('layui.pageGo')
    }
  })
}

/**
 * Translate laydate popup text.
 * Matches both original Chinese and already-translated text.
 */
function patchLaydate(container, t) {
  var footerBtns = container.querySelectorAll('.laydate-footer-btns span, .layui-laydate-footer span')
  if (footerBtns.length >= 3) {
    footerBtns[0].textContent = t('layui.dateClear')
    footerBtns[1].textContent = t('layui.dateNow')
    footerBtns[2].textContent = t('layui.dateConfirm')
  }
}

/**
 * Initialize MutationObserver to auto-patch Layui elements.
 * Call once after app.mount().
 */
export function initLayuiLocale() {
  var { t, locale } = useI18n()

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

  // Re-patch all when locale changes
  watch(locale, function () {
    patchAll()
  })

  setTimeout(patchAll, 500)
}
