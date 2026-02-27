<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()
let tableIns = null

onMounted(() => {
  createTemplate('tiersToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="add" title="${t('common.add')}"><i class="layui-icon layui-icon-add-1"></i></button>
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="${t('common.refresh')}"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)

  nextTick(() => {
    layui.use(['table'], (table) => {
      tableIns = renderTable(table, {
        elem: '#tiersTable',
        id: 'tiersTable',
        cols: [[
          { type: 'numbers', title: t('tiers.order'), width: 60 },
          { field: 'name', title: t('tiers.tierName'), minWidth: 200 },
          { field: 'created_at', title: t('tiers.createDate'), width: 200 },
        ]],
        data: [],
        page: false,
        toolbar: '#tiersToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: t('common.noData') },
      })

      table.on('toolbar(tiersTable)', (obj) => {
        if (obj.event === 'add') {
          layui.layer.msg(t('tiers.addTier'))
        } else if (obj.event === 'refresh') {
          table.reload('tiersTable')
        }
      })
    })
  })
})

</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-rate"></i> {{ t('tiers.title') }}
      </h3>
    </div>

    <table id="tiersTable" lay-filter="tiersTable"></table>
  </div>
</template>
