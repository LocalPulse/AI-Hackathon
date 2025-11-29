import { Link, useLocation } from 'react-router-dom'
import { useTranslation } from '@shared/i18n/hooks'
import { FaVideo, FaChartLine, FaList, FaCog } from 'react-icons/fa'
import './Sidebar.css'

const navItems = [
  { path: '/cameras', icon: FaVideo, key: 'cameras' },
  { path: '/metrics', icon: FaChartLine, key: 'metrics' },
  { path: '/logs', icon: FaList, key: 'logs' },
  { path: '/settings', icon: FaCog, key: 'settings' },
]

export const Sidebar = () => {
  const { t } = useTranslation()
  const location = useLocation()
  
  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        <ul className="sidebar-list">
          {navItems.map(item => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`sidebar-link ${isActive ? 'sidebar-link-active' : ''}`}
                >
                  <Icon className="sidebar-icon" />
                  <span>{t(`nav.${item.key}`)}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </aside>
  )
}

