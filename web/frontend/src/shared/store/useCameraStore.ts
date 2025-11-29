import { create } from 'zustand'
import type { Camera } from '@shared/api/types'

interface CameraStore {
  cameras: Camera[]
  setCameras: (cameras: Camera[]) => void
  updateCamera: (id: string, stats: Camera['stats']) => void
}

interface CachedCamera {
  camera: Camera
  lastSeen: number
  lastDataChange: number // When data (counts) last changed
  lastActiveTime: number // When camera was last active
}

const cameraCache = new Map<string, CachedCamera>()
const CACHE_TIMEOUT = 60000 // Keep camera in cache for 60 seconds after it disappears
const REMOVE_TIMEOUT = 300000 // Remove camera from cache after 5 minutes of absence
const RELOAD_TIMEOUT = 180000 // Reload page if no cameras for 3 minutes
const INACTIVE_DELAY = 45000 // Mark as inactive after 45 seconds of no updates
const DATA_CHANGE_TIMEOUT = 120000 // Consider inactive if no data changes for 2 minutes

let lastActiveCameraTime = Date.now()

// Cleanup old cameras from cache periodically
setInterval(() => {
  const now = Date.now()
  let hasActiveCameras = false
  
  cameraCache.forEach((value, cameraId) => {
    const timeSinceLastSeen = now - value.lastSeen
    if (timeSinceLastSeen > REMOVE_TIMEOUT) {
      cameraCache.delete(cameraId)
    } else if (value.camera.status === 'active') {
      hasActiveCameras = true
    }
  })
  
  if (hasActiveCameras) {
    lastActiveCameraTime = now
  } else {
    // Check if we should reload page
    const timeSinceLastActive = now - lastActiveCameraTime
    if (timeSinceLastActive > RELOAD_TIMEOUT && cameraCache.size === 0) {
      // No cameras for 3 minutes - reload page
      console.warn('No cameras detected for 3 minutes, reloading page...')
      window.location.reload()
    }
  }
}, 10000)

export const useCameraStore = create<CameraStore>((set, get) => ({
  cameras: [],
  setCameras: (cameras) => {
    const now = Date.now()
    const currentCameras = get().cameras
    const currentCamerasMap = new Map(currentCameras.map(c => [c.id, c]))
    
    const hasActiveCameras = cameras.some(c => c.status === 'active')
    if (hasActiveCameras) {
      lastActiveCameraTime = now
    }
    
    cameras.forEach(camera => {
      const currentCamera = currentCamerasMap.get(camera.id)
      const cached = cameraCache.get(camera.id)
      const dataChanged = !currentCamera || 
        currentCamera.stats.personCount !== camera.stats.personCount ||
        currentCamera.stats.trainCount !== camera.stats.trainCount ||
        currentCamera.status !== camera.status
      
      cameraCache.set(camera.id, {
        camera,
        lastSeen: now,
        lastDataChange: dataChanged ? now : (cached?.lastDataChange || now),
        lastActiveTime: camera.status === 'active' ? now : (cached?.lastActiveTime || now)
      })
    })
    
    const apiCameraIds = new Set(cameras.map(c => c.id))
    const cachedCameras = Array.from(cameraCache.entries())
      .filter(([cameraId]) => !apiCameraIds.has(cameraId))
      .map(([, value]) => {
        const timeSinceLastSeen = now - value.lastSeen
        const timeSinceLastActive = now - value.lastActiveTime
        const timeSinceDataChange = now - value.lastDataChange
        
        if (timeSinceLastSeen >= CACHE_TIMEOUT && 
            timeSinceLastActive >= INACTIVE_DELAY &&
            timeSinceDataChange >= DATA_CHANGE_TIMEOUT) {
          return null
        }
        
        const shouldBeActive = timeSinceLastActive < INACTIVE_DELAY || 
          timeSinceDataChange < DATA_CHANGE_TIMEOUT
        
        return {
          ...value.camera,
          status: shouldBeActive ? 'active' : 'inactive'
        }
      })
      .filter((camera): camera is Camera => camera !== null)
    
    const mergedCameras = [...cameras, ...cachedCameras]
      .sort((a, b) => a.id.localeCompare(b.id))
    
    set({ cameras: mergedCameras })
  },
  updateCamera: (id, stats) => {
    const now = Date.now()
    const state = get()
    const currentCamera = state.cameras.find(c => c.id === id)
    
    const dataChanged = !currentCamera ||
      currentCamera.stats.personCount !== stats.personCount ||
      currentCamera.stats.trainCount !== stats.trainCount
    
    const cached = cameraCache.get(id)
    if (cached) {
      cached.camera.stats = stats
      cached.lastSeen = now
      if (dataChanged) {
        cached.lastDataChange = now
      }
      if (cached.camera.status === 'active') {
        cached.lastActiveTime = now
      }
    }
    
    set({
      cameras: state.cameras.map((camera) =>
        camera.id === id ? { ...camera, stats } : camera
      ),
    })
  },
}))


