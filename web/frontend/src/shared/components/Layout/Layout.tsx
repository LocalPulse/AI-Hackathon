import type { ReactNode } from 'react'
import { Header } from '../Header/Header'
import { Sidebar } from '../Sidebar/Sidebar'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

export const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="layout-container">
      <Header />
      <div className="layout-content">
        <Sidebar />
        <main className="layout-main">
          {children}
        </main>
      </div>
    </div>
  )
}

