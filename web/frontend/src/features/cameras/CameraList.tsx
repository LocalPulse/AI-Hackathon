import { useMemo } from 'react'
import { useCameraStore } from '@shared/store'
import { useRealtimeStats, useCameraUpdates } from '@shared/hooks'
import { CameraCard } from './CameraCard'
import { useTranslation } from '@shared/i18n/hooks'
import { Spinner } from '@shared/components'

export const CameraList = () => {
  const { t } = useTranslation()
  const { cameras } = useCameraStore()
  
  useCameraUpdates()
  useRealtimeStats()
  
  const sortedCameras = useMemo(() => {
    return [...cameras].sort((a, b) => {
      if (a.status === 'active' && b.status !== 'active') return -1
      if (a.status !== 'active' && b.status === 'active') return 1
      return a.name.localeCompare(b.name)
    })
  }, [cameras])
  
  if (cameras.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner />
      </div>
    )
  }
  
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        {t('cameras.title')}
      </h2>
      
      {sortedCameras.length === 0 ? (
        <p className="text-gray-600 dark:text-gray-400">{t('cameras.noCameras')}</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedCameras.map(camera => (
            <CameraCard key={camera.id} camera={camera} />
          ))}
        </div>
      )}
    </div>
  )
}

