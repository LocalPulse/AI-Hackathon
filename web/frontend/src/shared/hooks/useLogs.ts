import { useEffect, useState } from 'react'
import { getLogs } from '@shared/api'
import type { LogFilters } from '@shared/api'
import { useLogsStore } from '@shared/store'

export const useLogs = (autoRefresh: boolean = true) => {
  const { logs, filters, limit, offset, setLogs } = useLogsStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const loadLogs = async (currentFilters?: LogFilters, currentLimit?: number, currentOffset?: number) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await getLogs(
        currentLimit ?? limit,
        currentOffset ?? offset,
        currentFilters ?? filters
      )
      setLogs(response.detections, response.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load logs')
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    loadLogs()
    
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadLogs()
      }, 5000)
      
      return () => clearInterval(interval)
    }
  }, [filters.classFilter, filters.activityFilter, filters.cameraId, limit, offset])
  
  return { logs, loading, error, loadLogs }
}

