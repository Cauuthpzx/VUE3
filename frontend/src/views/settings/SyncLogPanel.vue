<script setup>
import { nextTick, watch } from 'vue'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()

const props = defineProps({
  logs: { type: Array, required: true },
})

const emit = defineEmits(['clear'])

watch(() => props.logs.length, () => {
  nextTick(() => {
    const el = document.querySelector('.sync-log-body')
    if (el) el.scrollTop = el.scrollHeight
  })
})
</script>

<template>
  <div v-if="logs.length" class="tt-log">
    <div class="tt-log-header">
      <span class="tt-log-title"><i class="layui-icon layui-icon-log"></i> {{ t('settings.log') }}</span>
      <button class="layui-btn layui-btn-xs layui-btn-primary" @click="emit('clear')" style="opacity: 0.7"><i class="layui-icon layui-icon-delete"></i></button>
    </div>
    <div class="sync-log-body">
      <div v-for="(entry, i) in logs" :key="i" class="tt-log-line" :class="'log-' + entry.type">
        <span class="log-time">[{{ entry.time }}]</span>
        <span class="log-text">{{ entry.text }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tt-log { margin-top: 12px; border: 1px solid #e6e2da; border-radius: 4px; overflow: hidden; }
.tt-log-header { display: flex; align-items: center; justify-content: space-between; padding: 5px 12px; background: #2e2a25; }
.tt-log-title { font-size: 12px; font-weight: 600; color: #aaa; display: flex; align-items: center; gap: 5px; }
.tt-log-title .layui-icon { font-size: 14px; }
.sync-log-body { background: #1e1c19; padding: 8px 12px; max-height: 220px; overflow-y: auto; font-family: 'SF Mono', Consolas, Monaco, monospace; font-size: 11.5px; line-height: 1.7; }
.tt-log-line { display: flex; gap: 8px; white-space: pre-wrap; word-break: break-all; }
.log-time { color: #666; flex-shrink: 0; }
.log-info .log-text { color: #ddd; }
.log-ok .log-text { color: #5fb878; }
.log-warn .log-text { color: #ffb800; font-weight: 600; }
.log-error .log-text { color: #ff5722; font-weight: 600; }
</style>
