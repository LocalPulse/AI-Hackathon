import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@shared/theme'
import { MainLayout } from '@app/MainLayout'
import { CameraList } from '@features/cameras'
import { MetricsDashboard } from '@features/metrics'
import { LogsViewer } from '@features/logs'
import { SettingsPanel } from '@features/settings'
import { testApiConnection } from '@shared/api/health'
import '@shared/i18n/config'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function App() {
  useEffect(() => {
    const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'
    
    if (!USE_MOCK) {
      testApiConnection()
    } else {
      console.log('[App] Using mock data (VITE_USE_MOCK=true)')
    }
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Navigate to="/cameras" replace />} />
              <Route path="cameras" element={<CameraList />} />
              <Route path="metrics" element={<MetricsDashboard />} />
              <Route path="logs" element={<LogsViewer />} />
              <Route path="settings" element={<SettingsPanel />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
