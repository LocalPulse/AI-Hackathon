import { create } from 'zustand'
import type { Detection } from '@shared/api/types'

interface MetricsStore {
  detections: Detection[]
  setDetections: (detections: Detection[]) => void
  addDetection: (detection: Detection) => void
}

export const useMetricsStore = create<MetricsStore>((set) => ({
  detections: [],
  setDetections: (detections) => set({ detections }),
  addDetection: (detection) =>
    set((state) => ({
      detections: [detection, ...state.detections].slice(0, 1000),
    })),
}))

