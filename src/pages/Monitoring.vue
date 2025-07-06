<template>
  <v-card>
    <v-card-title>Sensor Monitoring</v-card-title>
    <v-data-table
      :headers="headers"
      :items="sensors"
      :items-per-page="10"
      class="elevation-1"
    >
      <template #item.latency="{ item }">
        <span :class="latencyColor(item.latency)">
          {{ item.latency.toFixed(2) }} s
        </span>
      </template>
      <template #item.enable="{ item }">
        <v-switch
          v-model="item.enable"
          @update:model-value="onToggle(item)"
          hide-details
        />
      </template>
    </v-data-table>
  </v-card>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const ws = ref(null)
const sensors = ref([])

const headers = [
  { title: 'ID', value: 'id' },
  { title: 'Last Topic', value: 'topic' },
  { title: 'Count', value: 'count' },
  { title: 'Latency', value: 'latency' },
  { title: 'QoS', value: 'qos' },
  { title: 'Enable', value: 'enable', sortable: false }
]

function latencyColor (val) {
  if (val < 1) return 'text-green'
  if (val < 2) return 'text-orange'
  return 'text-red'
}

function onToggle (sensor) {
  fetch(`/api/sensors/${sensor.id}/enable`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enable: sensor.enable })
  }).catch(err => console.error(err))
}

function connectWs () {
  ws.value = new WebSocket('/ws/monitor')
  ws.value.onmessage = event => {
    try {
      const data = JSON.parse(event.data)
      const idx = sensors.value.findIndex(s => s.id === data.sensor_id)
      const sensorData = {
        id: data.sensor_id,
        topic: data.topic || '',
        count: data.count || 0,
        latency: data.latency || 0,
        qos: data.qos || 0,
        enable: data.enable ?? true
      }
      if (idx === -1) {
        sensors.value.push(sensorData)
      } else {
        sensors.value[idx] = { ...sensors.value[idx], ...sensorData }
      }
    } catch (e) {
      console.error(e)
    }
  }
}

onMounted(connectWs)
onBeforeUnmount(() => {
  if (ws.value) {
    ws.value.close()
  }
})
</script>
