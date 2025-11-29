import { useEffect } from 'react'
import { getCameras } from '@shared/api/cameras'
import { useCameraStore } from '@shared/store'

export const useCameraUpdates = () => {
  const { setCameras } = useCameraStore()
  
  useEffect(() => {
    const loadCameras = async () => {
      const cameras = await getCameras()
      setCameras(cameras)
    }
    
    loadCameras()
  }, [setCameras])
}

