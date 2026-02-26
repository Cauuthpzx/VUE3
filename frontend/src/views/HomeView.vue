<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const authStore = useAuthStore()
const { userName } = storeToRefs(authStore)

onMounted(() => {
  layui.use([], () => {})
})

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="main-layout">
    <div class="layui-header" style="background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.08); padding: 0 20px; display: flex; align-items: center; justify-content: space-between;">
      <h3 style="margin: 0; font-size: 18px;">Dashboard</h3>
      <div>
        <span style="margin-right: 16px; color: #666;">Xin chào, <b>{{ userName }}</b></span>
        <button class="layui-btn layui-btn-sm layui-btn-primary" @click="handleLogout">
          Đăng xuất
        </button>
      </div>
    </div>

    <div style="padding: 24px;">
      <div class="layui-card">
        <div class="layui-card-header">Chào mừng</div>
        <div class="layui-card-body" style="padding: 24px;">
          <p>Bạn đã đăng nhập thành công.</p>
        </div>
      </div>
    </div>
  </div>
</template>
