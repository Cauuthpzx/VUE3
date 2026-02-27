<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { initDateRange } from '@/composables/useLayuiDate'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
const authStore = useAuthStore()

const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()
let tableIns = null

onMounted(() => {
  createTemplate('membersToolbar', `
    <div class="layui-btn-container">
      <button class="layui-btn layui-btn-xs" lay-event="addUser"><i class="layui-icon layui-icon-addition"></i>${t('members.addMember')}</button>
      <button class="layui-btn layui-btn-xs" lay-event="addAgent"><i class="layui-icon layui-icon-addition"></i>${t('members.addAgent')}</button>
    </div>
  `)
  createTemplate('membersRowBar', `
    <button class="layui-btn layui-btn-xs" lay-event="detail">${t('members.rebateSettings')}</button>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      tableIns = renderTable(table, {
        elem: '#membersTable',
        id: 'membersTable',
        cols: [[
          { field: '_agent_name', title: t('common.staff'), width: 110 },
          { field: 'username', title: t('members.member') },
          { field: 'type_format', title: t('members.memberType') },
          { field: 'parent_user', title: t('members.agentAccount') },
          { field: 'money', title: t('members.balance') },
          { field: 'deposit_count', title: t('members.depositCount') },
          { field: 'withdrawal_count', title: t('members.withdrawCount') },
          { field: 'deposit_amount', title: t('members.totalDeposit') },
          { field: 'withdrawal_amount', title: t('members.totalWithdraw') },
          { field: 'login_time', title: t('members.lastLogin') },
          { field: 'register_time', title: t('members.registerTime') },
          { field: 'status_format', title: t('common.status') },
          { title: t('common.actions'), toolbar: '#membersRowBar' },
        ]],
        url: '/api/v1/proxy/members',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        headers: { Authorization: 'Bearer ' + authStore.accessToken },
        parseData(res) {
          return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
        },
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#membersToolbar',
        defaultToolbar: ['filter', 'exports', 'print'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: t('common.noData') },
      })

      form.render()
      initDateRange('input[name="first_deposit_time"]', { value: '' })

      form.on('submit(searchMembers)', (data) => {
        table.reload('membersTable', {
          where: {
            username: data.field.username,
            status: data.field.status,
            sort_field: data.field.sort_field,
            sort_direction: data.field.sort_direction,
          }
        })
        return false
      })

      table.on('toolbar(membersTable)', (obj) => {
        if (obj.event === 'addUser') {
          layui.layer.msg(t('members.addMember'))
        } else if (obj.event === 'addAgent') {
          layui.layer.msg(t('members.addAgent'))
        }
      })

      table.on('tool(membersTable)', (obj) => {
        if (obj.event === 'detail') {
          layui.layer.msg(t('members.rebateSettings'))
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
        <i class="layui-icon layui-icon-friends"></i> {{ t('members.title') }}
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="membersSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>{{ t('members.accountName') }}</label>
            <input name="username" type="text" class="layui-input" :placeholder="t('members.enterAccountName')" />
          </div>
          <div class="data-search-field">
            <label>{{ t('members.firstDepositTime') }}</label>
            <input name="first_deposit_time" type="text" class="layui-input" :placeholder="t('common.startEnd')" readonly />
          </div>
          <div class="data-search-field">
            <label>{{ t('common.status') }}</label>
            <select name="status">
              <option value="">{{ t('common.select') }}</option>
              <option value="0">{{ t('members.statusUnrated') }}</option>
              <option value="1">{{ t('members.statusNormal') }}</option>
              <option value="2">{{ t('members.statusFrozen') }}</option>
              <option value="3">{{ t('members.statusLocked') }}</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>{{ t('members.sortField') }}</label>
            <select name="sort_field">
              <option value="">{{ t('common.select') }}</option>
              <option value="money">{{ t('members.balance') }}</option>
              <option value="login_time">{{ t('members.lastLogin') }}</option>
              <option value="register_time">{{ t('members.registerTime') }}</option>
              <option value="deposit_money">{{ t('members.totalDeposit') }}</option>
              <option value="withdrawal_money">{{ t('members.totalWithdraw') }}</option>
            </select>
          </div>
          <div class="data-search-field">
            <label>{{ t('members.sortDirection') }}</label>
            <select name="sort_direction">
              <option value="desc">{{ t('members.sortDesc') }}</option>
              <option value="asc">{{ t('members.sortAsc') }}</option>
            </select>
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchMembers">
            <i class="layui-icon layui-icon-search"></i> {{ t('common.search') }}
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> {{ t('common.reset') }}
          </button>
        </div>
      </form>
    </div>

    <table id="membersTable" lay-filter="membersTable"></table>
  </div>
</template>
