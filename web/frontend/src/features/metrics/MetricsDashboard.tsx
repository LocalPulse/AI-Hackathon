import { useMetrics } from '@shared/hooks'
import { useMetricsStore } from '@shared/store'
import { useEffect } from 'react'
import { getLogs } from '@shared/api'
import { Card } from '@shared/components'
import { useTranslation } from '@shared/i18n/hooks'
import { ConfidenceChart } from './ConfidenceChart'
import { ActivityDistribution } from './ActivityDistribution'
import { DetectionTimeline } from './DetectionTimeline'
import { ClassStatistics } from './ClassStatistics'

export const MetricsDashboard = () => {
  const { t } = useTranslation()
  const { setDetections } = useMetricsStore()
  const metrics = useMetrics()
  
  useEffect(() => {
    const loadDetections = async () => {
      const response = await getLogs(1000, 0)
      setDetections(response.detections)
    }
    
    loadDetections()
    
    const interval = setInterval(loadDetections, 10000)
    return () => clearInterval(interval)
  }, [setDetections])
  
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        {t('metrics.title')}
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <Card>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {t('metrics.totalDetections')}
          </p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {metrics.totalDetections}
          </p>
        </Card>
        
        <Card>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {t('metrics.averageConfidence')}
          </p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {(metrics.averageConfidence * 100).toFixed(1)}%
          </p>
        </Card>
        
        <Card>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {t('metrics.classStatistics')} - {t('metrics.person')}
          </p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {metrics.classDistribution.person}
          </p>
        </Card>
        
        <Card>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {t('metrics.classStatistics')} - {t('metrics.train')}
          </p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {metrics.classDistribution.train}
          </p>
        </Card>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <ActivityDistribution />
        <ClassStatistics />
      </div>
      
      <div className="grid grid-cols-1 gap-6">
        <ConfidenceChart />
        <DetectionTimeline />
      </div>
    </div>
  )
}

