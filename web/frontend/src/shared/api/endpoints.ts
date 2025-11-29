const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL
  
  if (envUrl) {
    return envUrl
  }
  
  if (import.meta.env.PROD) {
    return '/api'
  }
  
  return 'http://localhost:8000'
}

const API_BASE_URL = getApiBaseUrl()

if (import.meta.env.DEV) {
  console.log('[API Config] Base URL:', API_BASE_URL)
  console.log('[API Config] Environment:', import.meta.env.MODE)
  console.log('[API Config] VITE_API_URL:', import.meta.env.VITE_API_URL)
  console.log('[API Config] VITE_USE_MOCK:', import.meta.env.VITE_USE_MOCK)
}

export const endpoints = {
  stats: {
    current: `${API_BASE_URL}/stats/current`,
  },
  cameras: {
    list: `${API_BASE_URL}/cameras`,
    stats: (id: string) => `${API_BASE_URL}/cameras/${id}/stats`,
  },
  detections: {
    list: `${API_BASE_URL}/detections`,
  },
  health: `${API_BASE_URL}/health`,
} as const

export { API_BASE_URL }

