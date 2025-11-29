import { memo } from 'react'
import type { Camera } from '@shared/api/types'
import { Card, Badge } from '@shared/components'
import { useTranslation } from '@shared/i18n/hooks'
import { FaUsers, FaTrain, FaClock } from 'react-icons/fa'
import { formatDate } from '@shared/utils'

interface CameraCardProps {
  camera: Camera
}

export const CameraCard = memo(({ camera }: CameraCardProps) => {
  const { t } = useTranslation()
  
  const statusVariant = {
    active: 'success' as const,
    inactive: 'info' as const,
    error: 'error' as const,
  }
  
  return (
    <Card hover className="h-full">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {camera.name}
        </h3>
        <Badge variant={statusVariant[camera.status]}>
          {t(`cameras.${camera.status}`)}
        </Badge>
      </div>
      
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <FaUsers className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">{t('cameras.people')}</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {camera.stats.personCount}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <FaTrain className="w-5 h-5 text-green-600 dark:text-green-400" />
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">{t('cameras.trains')}</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {camera.stats.trainCount}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <FaClock className="w-4 h-4 text-gray-400" />
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">{t('cameras.lastUpdate')}</p>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              {formatDate(camera.stats.timestamp)}
            </p>
          </div>
        </div>
      </div>
    </Card>
  )
})

CameraCard.displayName = 'CameraCard'

