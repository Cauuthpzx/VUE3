<script setup>
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
</script>

<template>
  <div class="not-found">
    <div class="not-found-code">404</div>
    <div class="not-found-text">{{ t('router.notFound') }}</div>
    <router-link to="/" class="layui-btn layui-btn-normal layui-btn-sm">
      <i class="layui-icon layui-icon-home"></i> {{ t('router.backHome') }}
    </router-link>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  gap: 12px;
}
.not-found-code {
  font-size: 72px;
  font-weight: 800;
  color: #d2d2d2;
  line-height: 1;
}
.not-found-text {
  font-size: 16px;
  color: #999;
  margin-bottom: 8px;
}
</style>
