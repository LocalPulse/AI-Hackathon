import { useEffect, useRef } from 'react'
import { subscribeToCameraUpdates } from '@shared/api/cameras'
import { useCameraStore } from '@shared/store'

export const useRealtimeStats = () => {
  const { setCameras } = useCameraStore()
  const unsubscribeRef = useRef<(() => void) | null>(null)

  useEffect(() => {
    unsubscribeRef.current = subscribeToCameraUpdates((cameras) => {
      setCameras(cameras)
    })

    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current()
      }
    }
  }, [setCameras])
}

