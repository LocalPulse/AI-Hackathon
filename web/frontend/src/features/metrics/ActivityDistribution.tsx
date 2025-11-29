import { useMemo } from 'react'
import { Card } from '@shared/components'
import { useTranslation } from '@shared/i18n/hooks'
import { useMetricsStore } from '@shared/store'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b']

export const ActivityDistribution = () => {
  const { t } = useTranslation()
  const { detections } = useMetricsStore()
  
  const data = useMemo(() => {
    const distribution = detections.reduce(
      (acc, d) => {
        acc[d.activity] = (acc[d.activity] || 0) + 1
        return acc
      },
      {} as Record<string, number>
    )
    
    return [
      { name: t('metrics.standing'), value: distribution.standing || 0 },
      { name: t('metrics.moving'), value: distribution.moving || 0 },
      { name: t('metrics.stopped'), value: distribution.stopped || 0 },
    ]
  }, [detections, t])
  
  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        {t('metrics.activityDistribution')}
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}

