import type { Camera, CurrentStats } from './types'
import { endpoints } from './endpoints'
import client from './client'
import { mockCameras, startMockUpdates, stopMockUpdates } from './mock/data'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

interface ApiCamera {
  id: string
  name: string
  status: 'active' | 'inactive' | 'error'
  stats: {
    person_count: number
    train_count: number
    total_tracks: number
    timestamp: string
  }
}

interface CameraListResponse {
  cameras: ApiCamera[]
  total: number
}

interface ApiCurrentStats {
  person_count: number
  train_count: number
  total_tracks: number
  timestamp: string
}

const mapApiCameraToClient = (apiCamera: ApiCamera): Camera => {
  return {
    id: apiCamera.id,
    name: apiCamera.name,
    status: apiCamera.status,
    stats: {
      personCount: apiCamera.stats.person_count,
      trainCount: apiCamera.stats.train_count,
      totalTracks: apiCamera.stats.total_tracks,
      timestamp: apiCamera.stats.timestamp,
    },
  }
}

export const getCameras = async (): Promise<Camera[]> => {
  if (USE_MOCK) {
    return Promise.resolve([...mockCameras])
  }
  
  try {
    const response = await client.get<CameraListResponse>(endpoints.cameras.list)
    return response.data?.cameras?.map(mapApiCameraToClient) || []
  } catch (error) {
    console.error('Failed to fetch cameras:', error)
    return []
  }
}

export const getCameraStats = async (cameraId: string): Promise<CurrentStats | null> => {
  if (USE_MOCK) {
    const camera = mockCameras.find(c => c.id === cameraId)
    return camera ? camera.stats : null
  }
  
  try {
    const response = await client.get<ApiCurrentStats>(endpoints.cameras.stats(cameraId))
    
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
    console.error('Failed to fetch camera stats:', error)
    return null
  }
}

export const subscribeToCameraUpdates = (
  callback: (cameras: Camera[]) => void
): (() => void) => {
  if (USE_MOCK) {
    startMockUpdates(callback)
    return () => stopMockUpdates()
  }
  
  const interval = setInterval(async () => {
    const cameras = await getCameras()
    callback(cameras)
  }, 2000) // Update every 2 seconds (reduced frequency to prevent flickering)
  
  return () => clearInterval(interval)
}

