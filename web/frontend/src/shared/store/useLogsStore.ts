import { create } from 'zustand'
import type { Detection, LogFilters } from '@shared/api/types'

interface LogsStore {
  logs: Detection[]
  filters: LogFilters
  total: number
  limit: number
  offset: number
  setLogs: (logs: Detection[], total: number) => void
  setFilters: (filters: LogFilters) => void
  setPagination: (limit: number, offset: number) => void
  addLog: (log: Detection) => void
}

export const useLogsStore = create<LogsStore>((set) => ({
  logs: [],
  filters: {},
  total: 0,
  limit: 100,
  offset: 0,
  setLogs: (logs, total) => set({ logs, total }),
  setFilters: (filters) => set({ filters, offset: 0 }),
  setPagination: (limit, offset) => set({ limit, offset }),
  addLog: (log) =>
    set((state) => ({
      logs: [log, ...state.logs].slice(0, state.limit),
      total: state.total + 1,
    })),
}))

