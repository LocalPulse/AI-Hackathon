import { useMemo } from 'react'
import { Card, ChartTooltip } from '@shared/components'
import { useTranslation } from '@shared/i18n/hooks'
import { useCameraStore } from '@shared/store'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export const TopCameras = () => {
  const { t } = useTranslation()
  const { cameras } = useCameraStore()
  
  const chartData = useMemo(() => {
    return cameras
      .filter(c => c.status === 'active')
      .map(c => ({
        name: c.name,
        people: c.stats.personCount,
        trains: c.stats.trainCount,
        total: c.stats.totalTracks,
      }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 5)
  }, [cameras])
  
  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        {t('metrics.topCameras')}
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-300 dark:stroke-gray-700" />
          <XAxis dataKey="name" className="text-gray-600 dark:text-gray-400" angle={-45} textAnchor="end" height={100} />
          <YAxis className="text-gray-600 dark:text-gray-400" />
          <Tooltip content={<ChartTooltip />} />
          <Bar dataKey="people" stackId="a" fill="#3b82f6" name={t('cameras.people')} />
          <Bar dataKey="trains" stackId="a" fill="#10b981" name={t('cameras.trains')} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}

