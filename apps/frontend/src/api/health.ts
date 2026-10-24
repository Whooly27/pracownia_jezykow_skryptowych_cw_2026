import { apiGet } from './client'

export interface HealthResponse {
  status: 'ok' | 'degraded'
  database: 'ok' | 'unavailable'
}

export const fetchHealth = () => apiGet<HealthResponse>('/health/')
