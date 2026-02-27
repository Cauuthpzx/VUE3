<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import SvgIcon from '@/components/SvgIcon.vue'
import NavDropdown from '@/components/NavDropdown.vue'
import logoUrl from '@/assets/images/maxhub-logo.svg'
import { useI18n } from '@/composables/useI18n'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { userName } = storeToRefs(authStore)
const { t, locale, setLocale } = useI18n()

const openGroups = ref({})
const notifyCount = ref(0)

const languages = [
  { code: 'vi', label: 'Tiếng Việt' },
  { code: 'en', label: 'English' },
  { code: 'zh-CN', label: '中文' },
]

const langMenu = languages.map(l => ({
  key: l.code,
  label: l.label,
}))

function handleLangMenu(item) {
  setLocale(item.key)
}

const accountMenu = [
  { key: 'change-login-pw', labelKey: 'nav.changeLoginPw', icon: 'gear' },
  { key: 'change-trade-pw', labelKey: 'nav.changeTradePw', icon: 'gear' },
  { divider: true },
  { key: 'tiers', labelKey: 'nav.tiers', icon: 'gear' },
  { divider: true },
  { key: 'logout', labelKey: 'auth.logout', icon: 'sign-out' },
]

const sidebarItems = [
  { name: 'home', labelKey: 'nav.home', icon: 'home', route: '/', isSvg: true },
  {
    name: 'members-group', labelKey: 'nav.members', icon: 'layui-icon-friends',
    children: [
      { name: 'members', labelKey: 'nav.memberList', route: '/members' },
      { name: 'invites', labelKey: 'nav.inviteList', route: '/invites' },
    ]
  },
  {
    name: 'reports-group', labelKey: 'nav.reports', icon: 'layui-icon-chart',
    children: [
      { name: 'report-lottery', labelKey: 'nav.reportLottery', route: '/report-lottery' },
      { name: 'report-funds', labelKey: 'nav.reportFunds', route: '/report-funds' },
      { name: 'report-provider', labelKey: 'nav.reportProvider', route: '/report-provider' },
    ]
  },
  {
    name: 'finance-group', labelKey: 'nav.finance', icon: 'layui-icon-rmb',
    children: [
      { name: 'deposits', labelKey: 'nav.deposits', route: '/deposits' },
      { name: 'withdrawals', labelKey: 'nav.withdrawals', route: '/withdrawals' },
    ]
  },
  {
    name: 'bets-group', labelKey: 'nav.bets', icon: 'layui-icon-chart-screen',
    children: [
      { name: 'bets', labelKey: 'nav.betsLottery', route: '/bets' },
      { name: 'bet-third-party', labelKey: 'nav.betsThirdParty', route: '/bet-third-party' },
    ]
  },
  {
    name: 'rebate-group', labelKey: 'nav.rebate', icon: 'layui-icon-list',
    children: [
      { name: 'rebate', labelKey: 'nav.rebateRate', route: '/rebate' },
    ]
  },
  {
    name: 'settings-group', labelKey: 'nav.settings', icon: 'layui-icon-set',
    children: [
      { name: 'settings-system', labelKey: 'nav.settingsSystem', route: '/settings-system' },
      { name: 'settings-agents', labelKey: 'nav.settingsAgents', route: '/settings-agents' },
      { name: 'settings-account', labelKey: 'nav.settingsAccount', route: '/settings-account' },
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

// Update document title when locale changes (without navigation)
watch(locale, () => {
  if (route.meta.titleKey) {
    document.title = t(route.meta.titleKey)
  }
})

// Auto-open sidebar group when navigating to a child route
watch(() => route.path, () => {
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
              <span>{{ languages.find(l => l.code === locale)?.label }}</span>
            </template>
          </NavDropdown>
          <div class="app-notify-bell" v-tips="t('nav.notification')">
            <i class="layui-icon layui-icon-notice"></i>
            <span v-if="notifyCount > 0" class="app-notify-badge">{{ notifyCount > 99 ? '99+' : notifyCount }}</span>
          </div>
          <NavDropdown :items="accountMenu.map(i => i.divider ? i : { ...i, label: t(i.labelKey) })" @select="handleAccountMenu">
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
            <span class="app-sidebar-label">{{ t(item.labelKey) }}</span>
          </router-link>

          <!-- Group with children -->
          <div v-else class="app-sidebar-group" :class="{ active: isGroupActive(item) }">
            <div class="app-sidebar-group-title" @click="toggleGroup(item.name)">
              <i :class="['layui-icon', item.icon]" class="app-sidebar-icon app-sidebar-layui"></i>
              <span class="app-sidebar-label">{{ t(item.labelKey) }}</span>
            </div>
            <div class="app-sidebar-children" :class="{ open: openGroups[item.name] }">
              <router-link
                v-for="child in item.children"
                :key="child.name"
                :to="child.route"
                class="app-sidebar-child"
                :class="{ active: isItemActive(child) }"
              >
                {{ t(child.labelKey) }}
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
