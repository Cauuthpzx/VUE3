<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [String, Number], default: 16 },
  color: { type: String, default: 'currentColor' },
})

const iconModules = import.meta.glob('@/assets/icons/**/*.svg', {
  eager: true,
  query: '?url',
  import: 'default',
})

const iconUrl = computed(() => {
  for (const [path, url] of Object.entries(iconModules)) {
    const fileName = path.split('/').pop().replace('.svg', '')
    if (fileName === props.name) {
      return url
    }
  }
  return null
})

const sizeValue = computed(() =>
  typeof props.size === 'number' ? `${props.size}px` : props.size
)
</script>

<template>
  <img
    v-if="iconUrl"
    :src="iconUrl"
    :alt="name"
    class="svg-icon"
    :style="{ width: sizeValue, height: sizeValue }"
  />
</template>

<style scoped>
.svg-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}
</style>
