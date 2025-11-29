import client from './client'
import { endpoints, API_BASE_URL } from './endpoints'

interface HealthResponse {
  status: string
  database?: string
  service?: string
}

export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await client.get<HealthResponse>(endpoints.health)
    const isHealthy = response.data?.status === 'healthy'
    
    if (import.meta.env.DEV) {
      console.log('[API Health]', isHealthy ? '✅ Connected' : '❌ Unhealthy', response.data)
    }
    
    return isHealthy
  } catch (error) {
    console.error('[API Health] ❌ Connection failed:', error)
    return false
  }
}

export const testApiConnection = async (): Promise<void> => {
  const isHealthy = await checkApiHealth()
  
  if (!isHealthy) {
    console.warn('[API] API is not available.')
    console.warn('[API] Base URL:', API_BASE_URL)
    console.warn('[API] Health endpoint:', endpoints.health)
    console.warn('[API] Check if FastAPI is running and accessible.')
    console.warn('[API] To use mock data, set VITE_USE_MOCK=true in .env file.')
  } else {
    console.log('[API] Successfully connected to FastAPI at', API_BASE_URL)
  }
}

