import { useMemo } from 'react'
import { Card, ChartTooltip } from '@shared/components'
import { useTranslation } from '@shared/i18n/hooks'
import { useMetricsStore } from '@shared/store'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export const ConfidenceChart = () => {
  const { t } = useTranslation()
  const { detections } = useMetricsStore()
  
  const chartData = useMemo(() => {
    const recent = detections.slice(0, 50).reverse()
    return recent.map((d, index) => ({
      index,
      confidence: d.confidence * 100,
      timestamp: new Date(d.timestamp).toLocaleTimeString(),
    }))
  }, [detections])
  
  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        {t('metrics.averageConfidence')}
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-300 dark:stroke-gray-700" />
          <XAxis dataKey="timestamp" className="text-gray-600 dark:text-gray-400" />
          <YAxis className="text-gray-600 dark:text-gray-400" />
          <Tooltip 
            content={
              <ChartTooltip 
                valueFormatter={(v) => `${v.toFixed(2)}%`}
                nameFormatter={() => t('logs.confidence')}
              />
            } 
          />
          <Line
            type="monotone"
            dataKey="confidence"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  )
}

