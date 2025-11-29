export interface Camera {
  id: string
  name: string
  status: 'active' | 'inactive' | 'error'
  stats: CameraStats
}

export interface CameraStats {
  personCount: number
  trainCount: number
  totalTracks: number
  timestamp: string
}

export interface Detection {
  id: number
  trackId: number
  className: string
  activity: string
  confidence: number
  timestamp: string
  cameraId?: string
}

export interface DetectionResponse {
  total: number
  limit: number
  offset: number
  detections: Detection[]
}

export interface CurrentStats {
  personCount: number
  trainCount: number
  totalTracks: number
  timestamp: string
}

export interface LogFilters {
  classFilter?: string
  activityFilter?: string
  cameraId?: string
}

