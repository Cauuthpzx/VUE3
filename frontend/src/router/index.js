import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { titleKey: 'router.login', guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { titleKey: 'router.register', guest: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/views/HomeView.vue'),
        meta: { titleKey: 'router.home', requiresAuth: true },
      },
      // --- Members ---
      {
        path: 'members',
        name: 'members',
        component: () => import('@/views/members/MembersView.vue'),
        meta: { titleKey: 'router.members', requiresAuth: true },
      },
      {
        path: 'invites',
        name: 'invites',
        component: () => import('@/views/members/InvitesView.vue'),
        meta: { titleKey: 'router.invites', requiresAuth: true },
      },
      // --- Reports ---
      {
        path: 'report-lottery',
        name: 'report-lottery',
        component: () => import('@/views/reports/ReportLotteryView.vue'),
        meta: { titleKey: 'router.reportLottery', requiresAuth: true },
      },
      {
        path: 'report-funds',
        name: 'report-funds',
        component: () => import('@/views/reports/ReportFundsView.vue'),
        meta: { titleKey: 'router.reportFunds', requiresAuth: true },
      },
      {
        path: 'report-provider',
        name: 'report-provider',
        component: () => import('@/views/reports/ReportProviderView.vue'),
        meta: { titleKey: 'router.reportProvider', requiresAuth: true },
      },
      // --- Finance ---
      {
        path: 'deposits',
        name: 'deposits',
        component: () => import('@/views/finance/DepositsView.vue'),
        meta: { titleKey: 'router.deposits', requiresAuth: true },
      },
      {
        path: 'withdrawals',
        name: 'withdrawals',
        component: () => import('@/views/finance/WithdrawalsView.vue'),
        meta: { titleKey: 'router.withdrawals', requiresAuth: true },
      },
      // --- Bets ---
      {
        path: 'bets',
        name: 'bets',
        component: () => import('@/views/bets/BetsView.vue'),
        meta: { titleKey: 'router.betsLottery', requiresAuth: true },
      },
      {
        path: 'bet-third-party',
        name: 'bet-third-party',
        component: () => import('@/views/bets/BetThirdPartyView.vue'),
        meta: { titleKey: 'router.betsThirdParty', requiresAuth: true },
      },
      // --- Rebate ---
      {
        path: 'rebate',
        name: 'rebate',
        component: () => import('@/views/rebate/RebateView.vue'),
        meta: { titleKey: 'router.rebate', requiresAuth: true },
      },
      // --- Settings ---
      {
        path: 'settings-system',
        name: 'settings-system',
        component: () => import('@/views/settings/SettingsSystemView.vue'),
        meta: { titleKey: 'router.settingsSystem', requiresAuth: true },
      },
      {
        path: 'settings-agents',
        name: 'settings-agents',
        component: () => import('@/views/settings/SettingsAgentsView.vue'),
        meta: { titleKey: 'router.settingsAgents', requiresAuth: true },
      },
      {
        path: 'settings-account',
        name: 'settings-account',
        component: () => import('@/views/settings/SettingsAccountView.vue'),
        meta: { titleKey: 'router.settingsAccount', requiresAuth: true },
      },
      // --- Tiers ---
      {
        path: 'tiers',
        name: 'tiers',
        component: () => import('@/views/tiers/TiersView.vue'),
        meta: { titleKey: 'router.tiers', requiresAuth: true },
      },
      // --- Tools ---
      {
        path: 'change-login-pw',
        name: 'change-login-pw',
        component: () => import('@/views/tools/ChangeLoginPwView.vue'),
        meta: { titleKey: 'router.changeLoginPw', requiresAuth: true },
      },
      {
        path: 'change-trade-pw',
        name: 'change-trade-pw',
        component: () => import('@/views/tools/ChangeTradePwView.vue'),
        meta: { titleKey: 'router.changeTradePw', requiresAuth: true },
      },
      // --- Legacy (keep existing) ---
      {
        path: 'users',
        name: 'users',
        component: () => import('@/views/users/UsersView.vue'),
        meta: { titleKey: 'router.users', requiresAuth: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  // Resolve page title from locale
  const { t } = useI18n()
  document.title = to.meta.titleKey ? t(to.meta.titleKey) : 'App'

  const authStore = useAuthStore()

  // Chờ refresh token hoàn thành trước khi check auth
  await authStore.init()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
