/**
 * Tạo và inject <script type="text/html"> template vào document.body
 * để dùng với layui.table toolbar/templet.
 * Vue template không cho phép <script> tag bên trong.
 */
export function createTemplate(id, html) {
  let el = document.getElementById(id)
  if (el) el.remove()
  el = document.createElement('script')
  el.type = 'text/html'
  el.id = id
  el.innerHTML = html
  document.body.appendChild(el)
}

export function removeTemplate(id) {
  const el = document.getElementById(id)
  if (el) el.remove()
}
