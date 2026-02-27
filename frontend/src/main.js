import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { vTips, initGlobalTips } from '@/composables/useLayuiTips'
import { initLayuiLocale } from '@/composables/useLayuiLocale'
import './assets/css/app.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.directive('tips', vTips)
app.mount('#app')

// Global auto-tips for layui-rendered [title] buttons
initGlobalTips()

// Patch Layui built-in Chinese text (laypage, laydate)
initLayuiLocale()
