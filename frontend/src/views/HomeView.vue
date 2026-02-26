<script setup>
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'

const { userName } = storeToRefs(useAuthStore())
</script>

<template>
  <div class="layui-card">
    <div class="layui-card-header">Chào mừng</div>
    <div class="layui-card-body" style="padding: 24px;">
      <p>Xin chào, <b>{{ userName }}</b>. Bạn đã đăng nhập thành công.</p>
    </div>
  </div>
</template>
