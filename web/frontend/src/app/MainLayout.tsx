import { Layout } from '@shared/components'
import { Outlet } from 'react-router-dom'

export const MainLayout = () => {
  return (
    <Layout>
      <Outlet />
    </Layout>
  )
}

