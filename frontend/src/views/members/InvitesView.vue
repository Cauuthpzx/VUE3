<script setup>
import { onMounted, nextTick } from 'vue'
import { useLayuiTemplate } from '@/composables/useLayuiTemplate'
import { useLayuiTable } from '@/composables/useLayuiTable'
import { initDateRange } from '@/composables/useLayuiDate'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()
const { createTemplate } = useLayuiTemplate()
const { renderTable } = useLayuiTable()
onMounted(() => {
  createTemplate('invitesToolbar', `
    <button class="layui-btn layui-btn-xs" lay-event="add"><i class="layui-icon layui-icon-addition"></i>${t('invites.addInvite')}</button>
  `)
  createTemplate('invitesRowBar', `
    <button title="${t('common.copyLink')}" class="layui-btn layui-btn-xs layui-btn-normal" lay-event="copy">${t('common.copyLink')}</button>
    <button title="${t('members.rebateSettings')}" class="layui-btn layui-btn-xs layui-btn-warm" lay-event="setting">${t('common.viewSettings')}</button>
    <button title="${t('common.qrCode')}" class="layui-btn layui-btn-xs layui-btn-danger" lay-event="qr">${t('common.qrCode')}</button>
    <button title="${t('invites.editInvite')}" class="layui-btn layui-btn-xs" lay-event="edit">${t('invites.editInvite')}</button>
  `)

  nextTick(() => {
    layui.use(['table', 'form'], (table, form) => {
      renderTable(table, {
        elem: '#invitesTable',
        id: 'invitesTable',
        cols: [[
          { field: '_agent_name', title: t('common.staff'), width: 110 },
          { field: 'invite_code', title: t('invites.inviteCode') },
          { field: 'user_type', title: t('invites.inviteType') },
          { field: 'reg_count', title: t('invites.totalRegistered') },
          { field: 'scope_reg_count', title: t('invites.registeredUsers') },
          { field: 'recharge_count', title: t('invites.depositUsers') },
          { field: 'first_recharge_count', title: t('invites.firstDepositDay') },
          { field: 'register_recharge_count', title: t('invites.firstDepositRegDay') },
          { field: 'remark', title: t('invites.note') },
          { field: 'create_time', title: t('invites.addedTime') },
          { title: t('common.actions'), minWidth: 280, toolbar: '#invitesRowBar' },
        ]],
        url: '/api/v1/proxy/invites',
        method: 'post',
        contentType: 'application/x-www-form-urlencoded',
        parseData(res) {
          return { code: 0, data: res.data || [], count: res.count || 0, msg: '' }
        },
        page: { limit: 10, limits: [10, 50, 100, 200] },
        toolbar: '#invitesToolbar',
        defaultToolbar: ['filter'],
        skin: 'grid',
        even: true,
        size: 'sm',
        text: { none: t('common.noData') },
      })

      form.render()
      initDateRange('input[name="create_time"]')
      initDateRange('input[name="user_register_time"]')

      form.on('submit(searchInvites)', (data) => {
        table.reload('invitesTable', {
          where: {
            invite_code: data.field.invite_code,
            user_type: data.field.user_type,
          }
        })
        return false
      })

      table.on('toolbar(invitesTable)', (obj) => {
        if (obj.event === 'add') {
          layui.layer.msg(t('invites.addInvite'))
        }
      })

      table.on('tool(invitesTable)', (obj) => {
        if (obj.event === 'copy') {
          layui.layer.msg(t('common.copiedLink'))
        } else if (obj.event === 'setting') {
          layui.layer.msg(t('common.viewRebateSettings'))
        } else if (obj.event === 'qr') {
          layui.layer.msg(t('common.qrCode'))
        } else if (obj.event === 'edit') {
          layui.layer.msg(t('invites.editInviteCode'))
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
        <i class="layui-icon layui-icon-link"></i> {{ t('invites.title') }}
      </h3>
    </div>

    <div class="data-search-bar">
      <form class="layui-form" lay-filter="invitesSearch">
        <div class="data-search-fields">
          <div class="data-search-field">
            <label>{{ t('invites.addedTime') }}</label>
            <input name="create_time" type="text" class="layui-input" :placeholder="t('common.startEndTime')" readonly />
          </div>
          <div class="data-search-field">
            <label>{{ t('invites.memberLoginTime') }}</label>
            <input name="user_register_time" type="text" class="layui-input" :placeholder="t('common.startEndTime')" readonly />
          </div>
          <div class="data-search-field">
            <label>{{ t('invites.inviteCode') }}</label>
            <input name="invite_code" type="text" class="layui-input" :placeholder="t('invites.enterInviteCode')" />
          </div>
          <button class="layui-btn layui-btn-sm" lay-submit lay-filter="searchInvites">
            <i class="layui-icon layui-icon-search"></i> {{ t('common.search') }}
          </button>
          <button type="reset" class="layui-btn layui-btn-sm layui-btn-primary">
            <i class="layui-icon layui-icon-refresh"></i> {{ t('common.reset') }}
          </button>
        </div>
      </form>
    </div>

    <table id="invitesTable" lay-filter="invitesTable"></table>
  </div>
</template>
