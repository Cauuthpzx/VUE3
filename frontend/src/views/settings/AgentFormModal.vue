<script setup>
import { ref, nextTick, watch } from 'vue'
import { agentsApi } from '@/api/agents'
import { useI18n } from '@/composables/useI18n'

const { t } = useI18n()

const props = defineProps({
  visible: { type: Boolean, default: false },
  agent: { type: Object, default: null },
})

const emit = defineEmits(['update:visible', 'saved'])

const form = ref({ owner: '', username: '', base_url: '', password: '' })
const formError = ref('')

watch(() => props.visible, (val) => {
  if (!val) return
  if (props.agent) {
    form.value = { owner: props.agent.owner, username: props.agent.username, base_url: props.agent.base_url, password: '' }
  } else {
    form.value = { owner: '', username: '', base_url: 'https://a2u4k.ee88dly.com', password: '' }
  }
  formError.value = ''
  nextTick(() => layui.use(['form'], (f) => f.render()))
})

async function saveAgent() {
  formError.value = ''
  if (!form.value.owner.trim()) { formError.value = t('settings.ownerRequired'); return }
  if (!form.value.username.trim()) { formError.value = t('settings.usernameRequired2'); return }
  if (!form.value.base_url.trim()) { formError.value = t('settings.baseUrlRequired'); return }

  try {
    if (props.agent) {
      const payload = { owner: form.value.owner, base_url: form.value.base_url }
      if (form.value.password) payload.password = form.value.password
      const { data } = await agentsApi.update(props.agent.id, payload)
      if (data.code !== 0) { formError.value = data.message || t('settings.updateFailed'); return }
    } else {
      const payload = { owner: form.value.owner, username: form.value.username, base_url: form.value.base_url }
      if (form.value.password) payload.password = form.value.password
      const { data } = await agentsApi.create(payload)
      if (data.code !== 0) { formError.value = data.message || t('settings.createFailed'); return }
    }
    emit('update:visible', false)
    emit('saved')
  } catch (e) {
    formError.value = e.response?.data?.detail || t('settings.unknownError')
  }
}

function close() {
  emit('update:visible', false)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="agent-modal-overlay" @click.self="close">
      <div class="agent-modal">
        <div class="agent-modal-header">
          <h4>{{ agent ? t('settings.editAgent') : t('settings.addNewAgent') }}</h4>
          <i class="layui-icon layui-icon-close agent-modal-close" v-tips="t('common.cancel')" @click="close"></i>
        </div>
        <div class="agent-modal-body">
          <div v-if="formError" class="agent-form-error">
            <i class="layui-icon layui-icon-close-fill"></i> {{ formError }}
          </div>
          <div class="agent-form-field">
            <label>{{ t('settings.agentOwner') }}</label>
            <input v-model="form.owner" type="text" class="layui-input" :placeholder="t('settings.agentOwnerPlaceholder')" />
          </div>
          <div class="agent-form-field">
            <label>{{ t('settings.agentUsername') }}</label>
            <input v-model="form.username" type="text" class="layui-input" :placeholder="t('settings.agentUsernamePlaceholder')" :disabled="!!agent" />
          </div>
          <div class="agent-form-field">
            <label>{{ t('settings.agentBaseUrl') }}</label>
            <input v-model="form.base_url" type="text" class="layui-input" :placeholder="t('settings.agentBaseUrlPlaceholder')" />
          </div>
          <div class="agent-form-field">
            <label>{{ agent ? t('settings.agentPasswordKeep') : t('settings.agentPassword') }}</label>
            <input v-model="form.password" type="password" class="layui-input" :placeholder="t('settings.agentPasswordPlaceholder')" />
          </div>
        </div>
        <div class="agent-modal-footer">
          <button class="layui-btn layui-btn-sm layui-btn-primary" @click="close">{{ t('common.cancel') }}</button>
          <button class="layui-btn layui-btn-sm layui-btn-normal" @click="saveAgent">
            <i class="layui-icon layui-icon-ok"></i> {{ agent ? t('settings.updateBtn') : t('settings.createNew') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.agent-modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.35); z-index: 19999; display: flex; align-items: center; justify-content: center; }
.agent-modal { background: #fff; border-radius: 6px; width: 380px; max-width: 92vw; box-shadow: 0 6px 24px rgba(0,0,0,0.18); }
.agent-modal-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid #e6e2da; }
.agent-modal-header h4 { margin: 0; font-size: 14px; font-weight: 700; color: #2e2a25; }
.agent-modal-close { font-size: 16px; color: #999; cursor: pointer; transition: color 0.15s; }
.agent-modal-close:hover { color: #e74c3c; }
.agent-modal-body { padding: 14px 16px; display: flex; flex-direction: column; gap: 12px; }
.agent-form-error { display: flex; align-items: center; gap: 6px; background: rgba(231,76,60,0.06); border: 1px solid rgba(231,76,60,0.15); border-radius: 4px; color: #c0392b; padding: 7px 10px; font-size: 12px; }
.agent-form-error .layui-icon { font-size: 13px; }
.agent-form-field { display: flex; flex-direction: column; gap: 4px; }
.agent-form-field label { font-size: 12px; color: #666; font-weight: 600; }
.agent-form-field .layui-input { height: 32px; font-size: 13px; border-color: #e6e2da; }
.agent-form-field .layui-input:focus { border-color: #16baaa; }
.agent-form-field .layui-input:disabled { background: #f5f5f5; color: #999; }
.agent-modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 10px 16px; border-top: 1px solid #e6e2da; }
</style>
