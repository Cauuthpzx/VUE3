<script setup>
import SvgIcon from '@/components/SvgIcon.vue'

defineProps({
  items: {
    type: Array,
    required: true,
    // [{ label, icon, iconSize?, divider?, action? }]
  },
})

defineEmits(['select'])
</script>

<template>
  <div class="app-nav-dropdown">
    <a class="app-nav-dropdown-trigger">
      <slot name="trigger" />
      <i class="layui-icon layui-icon-triangle-d app-nav-arrow"></i>
    </a>
    <ul class="app-nav-dropdown-menu">
      <template v-for="(item, i) in items" :key="item.label || item.action || i">
        <li v-if="item.divider" class="app-nav-dropdown-divider"></li>
        <li v-else>
          <a @click="$emit('select', item)">
            <SvgIcon v-if="item.icon" :name="item.icon" :size="item.iconSize || 14" />
            <span>{{ item.label }}</span>
          </a>
        </li>
      </template>
    </ul>
  </div>
</template>
