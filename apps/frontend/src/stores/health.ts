import { ref } from 'vue'
import { defineStore } from 'pinia'

import { fetchHealth, type HealthResponse } from '@/api/health'

export const useHealthStore = defineStore('health', () => {
  const health = ref<HealthResponse | null>(null)
  const error = ref<string | null>(null)
  const loading = ref(false)

  async function refresh() {
    loading.value = true
    error.value = null
    try {
      health.value = await fetchHealth()
    } catch (e) {
      health.value = null
      error.value = e instanceof Error ? e.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { health, error, loading, refresh }
})
