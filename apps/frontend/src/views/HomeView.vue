<script setup lang="ts">
import { onMounted } from 'vue'

import { useHealthStore } from '@/stores/health'

const healthStore = useHealthStore()

onMounted(healthStore.refresh)
</script>

<template>
  <main>
    <h1>Pracownia Języków Skryptowych</h1>
    <section aria-live="polite">
      <p v-if="healthStore.loading">Checking backend…</p>
      <p v-else-if="healthStore.error" role="alert">Backend unreachable: {{ healthStore.error }}</p>
      <p v-else-if="healthStore.health">
        Backend: <strong>{{ healthStore.health.status }}</strong> · Database:
        <strong>{{ healthStore.health.database }}</strong>
      </p>
    </section>
  </main>
</template>
