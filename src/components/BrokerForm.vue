<template>
  <v-form ref="form" @submit.prevent="onSave">
    <v-text-field
      v-model="local.host"
      :rules="[rules.required]"
      label="Host"
      required
    />
    <v-text-field
      v-model.number="local.port"
      type="number"
      :rules="[rules.required, rules.port]"
      label="Port"
      required
    />
    <v-select
      v-model="local.security"
      :items="securities"
      label="Security"
    />
    <div v-if="local.security !== 'none'">
      <v-text-field v-model="local.username" label="Username" />
      <v-text-field v-model="local.password" type="password" label="Password" />
      <v-file-input v-model="local.cert" label="Certificate" />
    </div>
    <v-row class="mt-4" justify="end">
      <v-btn color="secondary" class="mr-2" @click="onCancel">Cancel</v-btn>
      <v-btn color="primary" @click="onSave">Save</v-btn>
    </v-row>
  </v-form>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      host: '',
      port: 1883,
      security: 'none',
      username: '',
      password: '',
      cert: null
    })
  }
})

const emit = defineEmits(['update:modelValue', 'save', 'cancel'])

const local = reactive({ ...props.modelValue })

watch(local, val => emit('update:modelValue', val), { deep: true })

const securities = ['none', 'tls']
const form = ref(null)

const rules = {
  required: v => !!v || 'Required',
  port: v => (v >= 1 && v <= 65535) || 'Port 1-65535'
}

function onSave () {
  if (form.value) {
    const { valid } = form.value.validate()
    if (!valid) return
  }
  emit('save', { ...local })
}

function onCancel () {
  emit('cancel')
}
</script>

