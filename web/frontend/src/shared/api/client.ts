import axios, { AxiosError } from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { endpoints } from './endpoints'

const getBaseURL = (): string => {
  const healthUrl = endpoints.health
  if (healthUrl.startsWith('/')) {
    return healthUrl.replace('/health', '')
  }
  const url = healthUrl.replace('/health', '')
  return url
}

const baseURL = getBaseURL()

if (import.meta.env.DEV) {
  console.log('[API Client] Base URL:', baseURL)
  console.log('[API Client] Health endpoint:', endpoints.health)
  console.log('[API Client] Use Mock:', import.meta.env.VITE_USE_MOCK === 'true')
}

const client: AxiosInstance = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (import.meta.env.DEV) {
      console.log('[API Request]', config.method?.toUpperCase(), config.url)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

client.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log('[API Response]', response.status, response.config.url)
    }
    return response
  },
  (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status
      const data = error.response.data as { error?: string; detail?: string }
      const url = error.config?.url || 'unknown'
      
      const errorMessage = data?.error || data?.detail || error.message
      
      console.error(`[API Error] ${status} ${url}:`, errorMessage)
      
      if (status === 401) {
        console.error('Unauthorized:', errorMessage)
      } else if (status === 403) {
        console.error('Forbidden:', errorMessage)
      } else if (status === 404) {
        console.error('Not found:', errorMessage, 'URL:', url)
      } else if (status >= 500) {
        console.error('Server error:', errorMessage)
      } else {
        console.error('API error:', errorMessage)
      }
    } else if (error.request) {
      console.error('[API Error] Network error: No response received', {
        url: error.config?.url,
        baseURL: error.config?.baseURL,
        method: error.config?.method,
      })
    } else {
      console.error('[API Error] Request error:', error.message)
    }
    
    return Promise.reject(error)
  }
)

export default client

