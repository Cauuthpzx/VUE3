<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import SvgIcon from '@/components/SvgIcon.vue'
import NavDropdown from '@/components/NavDropdown.vue'
import logoUrl from '@/assets/images/maxhub-logo.svg'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { userName } = storeToRefs(authStore)

const openGroups = ref({})
const notifyCount = ref(0)
const languages = [
  { code: 'vi', label: 'Tiếng Việt', flag: '🇻🇳' },
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'zh-CN', label: '中文', flag: '🇨🇳' },
]

const currentLang = ref(localStorage.getItem('lang') || 'vi')

function setLang(code) {
  currentLang.value = code
  localStorage.setItem('lang', code)
  window.location.reload()
}

const langMenu = languages.map(l => ({
  key: l.code,
  label: l.flag + ' ' + l.label,
}))

const currentLangLabel = computed(() => {
  const l = languages.find(l => l.code === currentLang.value)
  return l ? l.label : 'Language'
})

function handleLangMenu(item) {
  setLang(item.key)
}

const accountMenu = [
  { key: 'change-login-pw', label: 'Đổi MK đăng nhập', icon: 'gear' },
  { key: 'change-trade-pw', label: 'Đổi MK giao dịch', icon: 'gear' },
  { divider: true },
  { key: 'tiers', label: 'Cấp bậc', icon: 'gear' },
  { divider: true },
  { key: 'logout', label: 'Đăng xuất', icon: 'sign-out' },
]

const sidebarItems = [
  { name: 'home', label: 'Trang chủ', icon: 'home', route: '/', isSvg: true },
  {
    name: 'members-group', label: 'Thành viên', icon: 'layui-icon-friends',
    children: [
      { name: 'members', label: 'Danh sách', route: '/members' },
      { name: 'invites', label: 'Mã mời', route: '/invites' },
    ]
  },
  {
    name: 'reports-group', label: 'Báo cáo', icon: 'layui-icon-chart',
    children: [
      { name: 'report-lottery', label: 'Báo cáo Lottery', route: '/report-lottery' },
      { name: 'report-funds', label: 'Báo cáo Tài chính', route: '/report-funds' },
      { name: 'report-provider', label: 'Báo cáo NCC', route: '/report-provider' },
    ]
  },
  {
    name: 'finance-group', label: 'Tài chính', icon: 'layui-icon-rmb',
    children: [
      { name: 'deposits', label: 'Nạp tiền', route: '/deposits' },
      { name: 'withdrawals', label: 'Rút tiền', route: '/withdrawals' },
    ]
  },
  {
    name: 'bets-group', label: 'Cược', icon: 'layui-icon-chart-screen',
    children: [
      { name: 'bets', label: 'Cược Lottery', route: '/bets' },
      { name: 'bet-third-party', label: 'Cược bên thứ 3', route: '/bet-third-party' },
    ]
  },
  {
    name: 'rebate-group', label: 'Hoàn trả', icon: 'layui-icon-list',
    children: [
      { name: 'rebate', label: 'Tỷ lệ hoàn trả', route: '/rebate' },
    ]
  },
  {
    name: 'settings-group', label: 'Cài đặt', icon: 'layui-icon-set',
    children: [
      { name: 'settings-system', label: 'Hệ thống', route: '/settings-system' },
      { name: 'settings-agents', label: 'Agent & Đồng bộ', route: '/settings-agents' },
      { name: 'settings-account', label: 'Tài khoản', route: '/settings-account' },
    ]
  },
]

function isGroupActive(item) {
  if (!item.children) return false
  return item.children.some(c => route.path === c.route)
}

function isItemActive(item) {
  if (item.route === '/') return route.path === '/'
  return route.path === item.route
}

onMounted(() => {
  sidebarItems.forEach(item => {
    if (item.children && isGroupActive(item)) {
      openGroups.value[item.name] = true
    }
  })
})

function toggleGroup(name) {
  openGroups.value[name] = !openGroups.value[name]
}

async function handleAccountMenu(item) {
  if (item.key === 'logout') {
    await authStore.logout()
    router.push({ name: 'login' })
  } else if (item.key === 'change-login-pw') {
    router.push({ name: 'change-login-pw' })
  } else if (item.key === 'change-trade-pw') {
    router.push({ name: 'change-trade-pw' })
  } else if (item.key === 'tiers') {
    router.push({ name: 'tiers' })
  }
}
</script>

<template>
  <div class="app-layout">
    <!-- Header -->
    <header class="app-header">
      <div class="app-logo">
        <img :src="logoUrl" alt="MaxHUB" class="app-logo-img" />
      </div>
      <div class="app-header-content">
        <div class="app-header-right">
          <NavDropdown :items="langMenu" @select="handleLangMenu">
            <template #trigger>
              <SvgIcon name="globe" :size="18" />
              <span>{{ currentLangLabel }}</span>
            </template>
          </NavDropdown>
          <div class="app-notify-bell" title="Thông báo">
            <i class="layui-icon layui-icon-notice"></i>
            <span v-if="notifyCount > 0" class="app-notify-badge">{{ notifyCount > 99 ? '99+' : notifyCount }}</span>
          </div>
          <NavDropdown :items="accountMenu" @select="handleAccountMenu">
            <template #trigger>
              <i class="layui-icon layui-icon-github app-nav-avatar"></i>
              <span>{{ userName }}</span>
            </template>
          </NavDropdown>
        </div>
      </div>
    </header>

    <!-- Sidebar (hover expand) -->
    <aside class="app-sidebar">
      <nav class="app-sidebar-nav">
        <template v-for="item in sidebarItems" :key="item.name">
          <!-- Single item (no children) -->
          <router-link
            v-if="!item.children"
            :to="item.route"
            class="app-sidebar-item"
            :class="{ active: isItemActive(item) }"
          >
            <SvgIcon v-if="item.isSvg" :name="item.icon" :size="20" class="app-sidebar-icon" />
            <i v-else :class="['layui-icon', item.icon]" class="app-sidebar-icon app-sidebar-layui"></i>
            <span class="app-sidebar-label">{{ item.label }}</span>
          </router-link>

          <!-- Group with children -->
          <div v-else class="app-sidebar-group" :class="{ active: isGroupActive(item) }">
            <div class="app-sidebar-group-title" @click="toggleGroup(item.name)">
              <i :class="['layui-icon', item.icon]" class="app-sidebar-icon app-sidebar-layui"></i>
              <span class="app-sidebar-label">{{ item.label }}</span>
            </div>
            <div class="app-sidebar-children" :class="{ open: openGroups[item.name] }">
              <router-link
                v-for="child in item.children"
                :key="child.name"
                :to="child.route"
                class="app-sidebar-child"
                :class="{ active: isItemActive(child) }"
              >
                {{ child.label }}
              </router-link>
            </div>
          </div>
        </template>

      </nav>
    </aside>

    <!-- Content -->
    <main class="app-content">
      <div class="app-body-card">
        <router-view />
      </div>
    </main>
  </div>
</template>
