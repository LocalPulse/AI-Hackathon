import type { CurrentStats } from './types'
import { endpoints } from './endpoints'
import client from './client'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

interface ApiCurrentStats {
  person_count: number
  train_count: number
  total_tracks: number
  timestamp: string
}

export const getCurrentStats = async (): Promise<CurrentStats | null> => {
  if (USE_MOCK) {
    return {
      personCount: 35,
      trainCount: 3,
      totalTracks: 38,
      timestamp: new Date().toISOString(),
    }
  }
  
  try {
    const response = await client.get<ApiCurrentStats>(endpoints.stats.current)
    
    if (!response.data) {
      throw new Error('Invalid response format')
    }
    
    return {
      personCount: response.data.person_count,
      trainCount: response.data.train_count,
      totalTracks: response.data.total_tracks,
      timestamp: response.data.timestamp,
    }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
    return null
  }
}

