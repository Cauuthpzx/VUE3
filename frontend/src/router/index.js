import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: 'Đăng nhập', guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { title: 'Đăng ký', guest: true },
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
        meta: { title: 'Trang chủ', requiresAuth: true },
      },
      // --- Members ---
      {
        path: 'members',
        name: 'members',
        component: () => import('@/views/members/MembersView.vue'),
        meta: { title: 'Thành viên', requiresAuth: true },
      },
      {
        path: 'invites',
        name: 'invites',
        component: () => import('@/views/members/InvitesView.vue'),
        meta: { title: 'Mã mời', requiresAuth: true },
      },
      // --- Reports ---
      {
        path: 'report-lottery',
        name: 'report-lottery',
        component: () => import('@/views/reports/ReportLotteryView.vue'),
        meta: { title: 'Báo cáo Lottery', requiresAuth: true },
      },
      {
        path: 'report-funds',
        name: 'report-funds',
        component: () => import('@/views/reports/ReportFundsView.vue'),
        meta: { title: 'Báo cáo Tài chính', requiresAuth: true },
      },
      {
        path: 'report-provider',
        name: 'report-provider',
        component: () => import('@/views/reports/ReportProviderView.vue'),
        meta: { title: 'Báo cáo Nhà cung cấp', requiresAuth: true },
      },
      // --- Finance ---
      {
        path: 'deposits',
        name: 'deposits',
        component: () => import('@/views/finance/DepositsView.vue'),
        meta: { title: 'Nạp tiền', requiresAuth: true },
      },
      {
        path: 'withdrawals',
        name: 'withdrawals',
        component: () => import('@/views/finance/WithdrawalsView.vue'),
        meta: { title: 'Lịch sử rút tiền', requiresAuth: true },
      },
      // --- Bets ---
      {
        path: 'bets',
        name: 'bets',
        component: () => import('@/views/bets/BetsView.vue'),
        meta: { title: 'Cược Lottery', requiresAuth: true },
      },
      {
        path: 'bet-third-party',
        name: 'bet-third-party',
        component: () => import('@/views/bets/BetThirdPartyView.vue'),
        meta: { title: 'Cược bên thứ ba', requiresAuth: true },
      },
      // --- Rebate ---
      {
        path: 'rebate',
        name: 'rebate',
        component: () => import('@/views/rebate/RebateView.vue'),
        meta: { title: 'Tỷ lệ hoàn trả', requiresAuth: true },
      },
      // --- Settings ---
      {
        path: 'settings-system',
        name: 'settings-system',
        component: () => import('@/views/settings/SettingsSystemView.vue'),
        meta: { title: 'Cài đặt hệ thống', requiresAuth: true },
      },
      {
        path: 'settings-sync',
        name: 'settings-sync',
        component: () => import('@/views/settings/SettingsSyncView.vue'),
        meta: { title: 'Đồng bộ Agent', requiresAuth: true },
      },
      {
        path: 'settings-account',
        name: 'settings-account',
        component: () => import('@/views/settings/SettingsAccountView.vue'),
        meta: { title: 'Quản lý tài khoản', requiresAuth: true },
      },
      // --- Tiers ---
      {
        path: 'tiers',
        name: 'tiers',
        component: () => import('@/views/tiers/TiersView.vue'),
        meta: { title: 'Cấp bậc', requiresAuth: true },
      },
      // --- Tools ---
      {
        path: 'change-login-pw',
        name: 'change-login-pw',
        component: () => import('@/views/tools/ChangeLoginPwView.vue'),
        meta: { title: 'Đổi mật khẩu đăng nhập', requiresAuth: true },
      },
      {
        path: 'change-trade-pw',
        name: 'change-trade-pw',
        component: () => import('@/views/tools/ChangeTradePwView.vue'),
        meta: { title: 'Đổi mật khẩu giao dịch', requiresAuth: true },
      },
      // --- Legacy (keep existing) ---
      {
        path: 'users',
        name: 'users',
        component: () => import('@/views/users/UsersView.vue'),
        meta: { title: 'Quản lý người dùng', requiresAuth: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title || 'App'

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
