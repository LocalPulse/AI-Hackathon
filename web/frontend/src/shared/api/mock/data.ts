import type { Camera, Detection } from '../types'

const generateMockDetections = (count: number, cameraId?: string): Detection[] => {
  const activities = ['standing', 'moving', 'stopped']
  const classes = ['person', 'train']
  const detections: Detection[] = []
  
  const now = Date.now()
  
  for (let i = 0; i < count; i++) {
    detections.push({
      id: i + 1,
      trackId: Math.floor(Math.random() * 100) + 1,
      className: classes[Math.floor(Math.random() * classes.length)],
      activity: activities[Math.floor(Math.random() * activities.length)],
      confidence: Math.random() * 0.4 + 0.6,
      timestamp: new Date(now - Math.random() * 3600000).toISOString(),
      cameraId,
    })
  }
  
  return detections.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
}

export const mockCameras: Camera[] = [
  {
    id: 'camera-1',
    name: 'Platform 1 - Main Entrance',
    status: 'active',
    stats: {
      personCount: 12,
      trainCount: 2,
      totalTracks: 14,
      timestamp: new Date().toISOString(),
    },
  },
  {
    id: 'camera-2',
    name: 'Platform 2 - Waiting Area',
    status: 'active',
    stats: {
      personCount: 8,
      trainCount: 1,
      totalTracks: 9,
      timestamp: new Date().toISOString(),
    },
  },
  {
    id: 'camera-3',
    name: 'Platform 3 - Exit',
    status: 'active',
    stats: {
      personCount: 15,
      trainCount: 0,
      totalTracks: 15,
      timestamp: new Date().toISOString(),
    },
  },
  {
    id: 'camera-4',
    name: 'Platform 4 - Storage',
    status: 'inactive',
    stats: {
      personCount: 0,
      trainCount: 0,
      totalTracks: 0,
      timestamp: new Date().toISOString(),
    },
  },
  {
    id: 'camera-5',
    name: 'Platform 5 - Maintenance',
    status: 'error',
    stats: {
      personCount: 0,
      trainCount: 0,
      totalTracks: 0,
      timestamp: new Date().toISOString(),
    },
  },
]

export const mockDetections = generateMockDetections(200)

let updateInterval: number | null = null

export const startMockUpdates = (callback: (cameras: Camera[]) => void) => {
  if (updateInterval) return
  
  updateInterval = window.setInterval(() => {
    const updated = mockCameras.map(camera => {
      if (camera.status !== 'active') return camera
      
      const change = Math.floor(Math.random() * 3) - 1
      const newPersonCount = Math.max(0, camera.stats.personCount + change)
      const trainChange = Math.random() > 0.9 ? (Math.random() > 0.5 ? 1 : -1) : 0
      const newTrainCount = Math.max(0, camera.stats.trainCount + trainChange)
      
      return {
        ...camera,
        stats: {
          personCount: newPersonCount,
          trainCount: newTrainCount,
          totalTracks: newPersonCount + newTrainCount,
          timestamp: new Date().toISOString(),
        },
      }
    })
    
    callback(updated)
  }, 3000)
}

export const stopMockUpdates = () => {
  if (updateInterval) {
    clearInterval(updateInterval)
    updateInterval = null
  }
}

