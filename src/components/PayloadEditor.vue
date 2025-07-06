<template>
  <div>
    <v-tabs v-model="tab" grow>
      <v-tab :value="0">{{ t('payloadEditor.graphic') }}</v-tab>
      <v-tab :value="1">{{ t('payloadEditor.code') }}</v-tab>
    </v-tabs>
    <v-window v-model="tab" class="mt-2">
      <v-window-item :value="0">
        <Vue3JsonEditor
          v-model="currentValue"
          :dark="isDark"
        />
      </v-window-item>
      <v-window-item :value="1">
        <MonacoEditor
          v-model="code"
          language="json"
          :theme="isDark ? 'vs-dark' : 'vs-light'"
          class="editor"
        />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTheme } from 'vuetify'
import { Vue3JsonEditor } from 'vue3-json-editor'
import MonacoEditor from '@monaco-editor/vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const tab = ref(0)
const currentValue = ref(structuredClone(props.modelValue))
const code = ref(JSON.stringify(currentValue.value, null, 2))

watch(() => props.modelValue, val => {
  currentValue.value = structuredClone(val)
  code.value = JSON.stringify(val, null, 2)
}, { deep: true })

watch(currentValue, val => {
  code.value = JSON.stringify(val, null, 2)
  emit('update:modelValue', val)
}, { deep: true })

watch(code, val => {
  try {
    const obj = JSON.parse(val)
    currentValue.value = obj
    emit('update:modelValue', obj)
  } catch (e) { /* ignore parse errors */ }
})

const theme = useTheme()
const isDark = computed(() => theme.current.value.dark)

const { t } = useI18n({
  messages: {
    en: { payloadEditor: { graphic: 'Graphic', code: 'Code' } },
    fr: { payloadEditor: { graphic: 'Graphique', code: 'Code' } }
  }
})
</script>

<style scoped>
.editor {
  height: 400px;
}
</style>
