import { useMemo } from 'react'
import { useMetricsStore } from '@shared/store'

export const useMetrics = () => {
  const { detections } = useMetricsStore()
  
  const metrics = useMemo(() => {
    if (detections.length === 0) {
      return {
        totalDetections: 0,
        averageConfidence: 0,
        activityDistribution: { standing: 0, moving: 0, stopped: 0 },
        classDistribution: { person: 0, train: 0 },
      }
    }
    
    const totalDetections = detections.length
    const averageConfidence =
      detections.reduce((sum, d) => sum + d.confidence, 0) / totalDetections
    
    const activityDistribution = detections.reduce(
      (acc, d) => {
        acc[d.activity as keyof typeof acc] = (acc[d.activity as keyof typeof acc] || 0) + 1
        return acc
      },
      { standing: 0, moving: 0, stopped: 0 }
    )
    
    const classDistribution = detections.reduce(
      (acc, d) => {
        acc[d.className as keyof typeof acc] = (acc[d.className as keyof typeof acc] || 0) + 1
        return acc
      },
      { person: 0, train: 0 }
    )
    
    return {
      totalDetections,
      averageConfidence,
      activityDistribution,
      classDistribution,
    }
  }, [detections])
  
  return metrics
}

