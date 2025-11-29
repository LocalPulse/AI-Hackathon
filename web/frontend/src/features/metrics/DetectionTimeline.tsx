import { useMemo } from 'react'
import { Card, ChartTooltip } from '@shared/components'
import { useTranslation } from '@shared/i18n/hooks'
import { useMetricsStore } from '@shared/store'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export const DetectionTimeline = () => {
  const { t } = useTranslation()
  const { detections } = useMetricsStore()
  
  const chartData = useMemo(() => {
    const now = Date.now()
    const hours = Array.from({ length: 24 }, (_, i) => {
      const hourStart = now - (23 - i) * 3600000
      const hourEnd = hourStart + 3600000
      const count = detections.filter(
        d => {
          const time = new Date(d.timestamp).getTime()
          return time >= hourStart && time < hourEnd
        }
      ).length
      
      return {
        hour: new Date(hourStart).toLocaleTimeString('en-US', { hour: 'numeric' }),
        count,
      }
    })
    
    return hours
  }, [detections])
  
  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        {t('metrics.detectionTimeline')}
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-300 dark:stroke-gray-700" />
          <XAxis dataKey="hour" className="text-gray-600 dark:text-gray-400" />
          <YAxis className="text-gray-600 dark:text-gray-400" />
          <Tooltip 
            content={
              <ChartTooltip 
                nameFormatter={() => t('metrics.totalDetections')}
              />
            } 
          />
          <Bar dataKey="count" fill="#3b82f6" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}

