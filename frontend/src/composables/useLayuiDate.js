/**
 * Format Date → dd/MM/yyyy
 */
function fmt(d) {
  var dd = String(d.getDate()).padStart(2, '0')
  var mm = String(d.getMonth() + 1).padStart(2, '0')
  return dd + '/' + mm + '/' + d.getFullYear()
}

/**
 * Tính khoảng ngày theo key chọn nhanh.
 * Trả về "dd/MM/yyyy - dd/MM/yyyy" hoặc '' nếu key rỗng.
 */
export function quickDateValue(key) {
  var now = new Date()
  var y = now.getFullYear()
  var m = now.getMonth()
  var d = now.getDate()

  switch (key) {
    case 'today':
      return fmt(now) + ' - ' + fmt(now)
    case 'yesterday': {
      var yd = new Date(y, m, d - 1)
      return fmt(yd) + ' - ' + fmt(yd)
    }
    case '7days':
      return fmt(new Date(y, m, d - 6)) + ' - ' + fmt(now)
    case 'thisMonth':
      return fmt(new Date(y, m, 1)) + ' - ' + fmt(new Date(y, m + 1, 0))
    case 'lastMonth':
      return fmt(new Date(y, m - 1, 1)) + ' - ' + fmt(new Date(y, m, 0))
    default:
      return ''
  }
}

/**
 * Khởi tạo layui.laydate date range picker — hiển thị 1 panel duy nhất.
 * Không có shortcuts trong panel (tách riêng ra dropdown).
 */
export function initDateRange(selector, options = {}) {
  var userReady = options.ready
  delete options.ready

  // Mặc định value = hôm nay nếu không truyền
  if (!options.value) {
    options.value = quickDateValue('today')
  }

  layui.use('laydate', (laydate) => {
    laydate.render(
      Object.assign(
        {
          type: 'date',
          range: true,
          rangeLinked: true,
          format: 'dd/MM/yyyy'
        },
        options,
        {
          elem: selector,
          ready: function () {
            var input = document.querySelector(selector)
            if (input) {
              var key = input.getAttribute('lay-key')
              var el = document.getElementById('layui-laydate' + key)
              if (el) el.classList.add('laydate-single-panel')
            }
            if (userReady) userReady.apply(this, arguments)
          }
        }
      )
    )
  })
}
