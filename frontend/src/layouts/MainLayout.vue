<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import SvgIcon from '@/components/SvgIcon.vue'
import NavDropdown from '@/components/NavDropdown.vue'

const SIDEBAR_KEY = 'sidebar_collapsed'

const router = useRouter()
const authStore = useAuthStore()
const { userName } = storeToRefs(authStore)

const collapsed = ref(false)

const accountMenu = [
  { key: 'settings', label: 'Cài đặt', icon: 'gear' },
  { divider: true },
  { key: 'logout', label: 'Đăng xuất', icon: 'sign-out' },
]

const sidebarItems = [
  { name: 'home', label: 'Trang chủ', icon: 'home', route: '/' },
  { name: 'users', label: 'Người dùng', icon: 'layui-icon-friends', route: '/users' },
]

onMounted(() => {
  collapsed.value = localStorage.getItem(SIDEBAR_KEY) === '1'
})

function toggleSidebar() {
  collapsed.value = !collapsed.value
  localStorage.setItem(SIDEBAR_KEY, collapsed.value ? '1' : '0')
}

async function handleAccountMenu(item) {
  if (item.key === 'logout') {
    await authStore.logout()
    router.push({ name: 'login' })
  }
}
</script>

<template>
  <div class="app-layout">
    <!-- Header -->
    <header class="app-header">
      <div class="app-logo" :class="{ collapsed }">
        <span v-if="!collapsed" class="app-logo-text">MODULES</span>
        <span v-else class="app-logo-text-mini">M</span>
      </div>
      <div class="app-header-content">
        <button class="app-header-toggle" @click="toggleSidebar">
          <SvgIcon name="three-bars" :size="18" />
        </button>
        <div class="app-header-right">
          <NavDropdown :items="accountMenu" @select="handleAccountMenu">
            <template #trigger>
              <i class="layui-icon layui-icon-github app-nav-avatar"></i>
              <span>{{ userName }}</span>
            </template>
          </NavDropdown>
        </div>
      </div>
    </header>

    <!-- Sidebar -->
    <aside class="app-sidebar" :class="{ collapsed }">
      <nav class="app-sidebar-nav">
        <router-link
          v-for="item in sidebarItems"
          :key="item.name"
          :to="item.route"
          class="app-sidebar-item"
          :class="{ active: $route.path === item.route }"
        >
          <i v-if="item.icon.startsWith('layui-icon-')" :class="['layui-icon', item.icon]" class="app-sidebar-icon app-sidebar-layui"></i>
          <SvgIcon v-else :name="item.icon" :size="20" class="app-sidebar-icon" />
          <span v-if="!collapsed" class="app-sidebar-label">{{ item.label }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- Content -->
    <main class="app-content" :class="{ collapsed }">
      <router-view />
    </main>
  </div>
</template>
