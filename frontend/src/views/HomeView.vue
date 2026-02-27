<script setup>
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'

const { userName } = storeToRefs(useAuthStore())
const { t } = useI18n()
</script>

<template>
  <div class="layui-card">
    <div class="layui-card-header">{{ t('home.welcome') }}</div>
    <div class="layui-card-body" style="padding: 24px;">
      <p>{{ t('home.greeting', { name: userName }) }}</p>
    </div>
  </div>
</template>
