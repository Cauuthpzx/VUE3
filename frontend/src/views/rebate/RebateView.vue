<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
const { createTemplate } = useLayuiTemplate()
const { renderTable, reloadTable, onLocaleChange } = useLayuiTable()

function initTemplates() {
  createTemplate('rebateToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="refresh" title="${t('common.refresh')}"><i class="layui-icon layui-icon-refresh"></i></button>
    </div>
  `)
}

function getCols() {
  return [[
    { field: 'odds_11', title: t('rebate.gameType'), width: 130 },
    { field: 'odds_10', title: t('rebate.level', { n: 10 }), width: 80 },
    { field: 'odds_9', title: t('rebate.level', { n: 9 }), width: 80 },
    { field: 'odds_8', title: t('rebate.level', { n: 8 }), width: 80 },
    { field: 'odds_7', title: t('rebate.level', { n: 7 }), width: 80 },
    { field: 'odds_6', title: t('rebate.level', { n: 6 }), width: 80 },
    { field: 'odds_5', title: t('rebate.level', { n: 5 }), width: 80 },
    { field: 'odds_4', title: t('rebate.level', { n: 4 }), width: 80 },
    { field: 'odds_3', title: t('rebate.level', { n: 3 }), width: 80 },
    { field: 'odds_2', title: t('rebate.level', { n: 2 }), width: 80 },
    { field: 'odds_1', title: t('rebate.level', { n: 1 }), width: 80 },
  ]]
}

function initTable(table) {
  initTemplates()
  renderTable(table, {
    elem: '#rebateTable',
    id: 'rebateTable',
    cols: getCols(),
    data: [],
    page: false,
    toolbar: '#rebateToolbar',
    defaultToolbar: ['filter', 'exports', 'print'],
    skin: 'grid',
    even: true,
    size: 'sm',
    text: { none: t('common.noData') },
  })
}

onMounted(() => {
  nextTick(() => {
    layui.use(['table'], (table) => {
      initTable(table)

      table.on('toolbar(rebateTable)', (obj) => {
        if (obj.event === 'refresh') {
          table.reload('rebateTable')
        }
      })
    })
  })
})

onLocaleChange(() => {
  initTemplates()
  layui.use(['table'], (table) => {
    reloadTable(table, 'rebateTable', {
      cols: getCols(),
      toolbar: '#rebateToolbar',
      defaultToolbar: ['filter', 'exports', 'print'],
      text: { none: t('common.noData') },
    })
  })
})

</script>

<template>
  <div class="data-page">
    <div class="data-page-header">
      <h3 class="data-page-title">
        <i class="layui-icon layui-icon-list"></i> {{ t('rebate.title') }}
      </h3>
    </div>

    <table id="rebateTable" lay-filter="rebateTable"></table>
  </div>
</template>
