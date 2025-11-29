import type { DetectionResponse, LogFilters, Detection } from './types'
import { endpoints } from './endpoints'
import client from './client'
import { mockDetections } from './mock/data'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

interface ApiDetection {
  id: number
  track_id: number
  class_name: string
  activity: string
  confidence: number
  timestamp: string
  camera_id?: string
}

interface ApiDetectionResponse {
  total: number
  limit: number
  offset: number
  detections: ApiDetection[]
}

const mapApiDetectionToClient = (apiDetection: ApiDetection): Detection => {
  return {
    id: apiDetection.id,
    trackId: apiDetection.track_id,
    className: apiDetection.class_name,
    activity: apiDetection.activity,
    confidence: apiDetection.confidence,
    timestamp: apiDetection.timestamp,
    cameraId: apiDetection.camera_id,
  }
}

export const getLogs = async (
  limit: number = 100,
  offset: number = 0,
  filters?: LogFilters
): Promise<DetectionResponse> => {
  if (USE_MOCK) {
    let filtered = [...mockDetections]
    
    if (filters?.classFilter) {
      filtered = filtered.filter(d => d.className === filters.classFilter)
    }
    
    if (filters?.activityFilter) {
      filtered = filtered.filter(d => d.activity === filters.activityFilter)
    }
    
    if (filters?.cameraId) {
      filtered = filtered.filter(d => d.cameraId === filters.cameraId)
    }
    
    const paginated = filtered.slice(offset, offset + limit)
    
    return {
      total: filtered.length,
      limit,
      offset,
      detections: paginated,
    }
  }
  
  try {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    })
    
    if (filters?.classFilter) {
      params.append('class_filter', filters.classFilter)
    }
    
    if (filters?.activityFilter) {
      params.append('activity_filter', filters.activityFilter)
    }
    
    if (filters?.cameraId) {
      params.append('camera_id', filters.cameraId)
    }
    
    const response = await client.get<ApiDetectionResponse>(`${endpoints.detections.list}?${params}`)
    
    if (!response.data || !Array.isArray(response.data.detections)) {
      throw new Error('Invalid response format')
    }
    
    return {
      total: response.data.total,
      limit: response.data.limit,
      offset: response.data.offset,
      detections: response.data.detections.map(mapApiDetectionToClient),
    }
  } catch (error) {
    console.error('Failed to fetch logs:', error)
    return {
      total: 0,
      limit,
      offset,
      detections: [],
    }
  }
}

