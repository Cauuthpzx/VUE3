<script setup>
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-set"></i> {{ t('settings.system') }}
      </h3>
    </div>
    <div class="layui-card">
      <div class="layui-card-body placeholder-card">
        <div class="placeholder-icon">
          <i class="layui-icon layui-icon-set" style="font-size: 48px; color: #ccc;"></i>
        </div>
        <p class="placeholder-text">{{ t('settings.systemDev') }}</p>
        <p class="placeholder-desc">{{ t('settings.systemDevDesc') }}</p>
      </div>
    </div>
  </div>
</template>
