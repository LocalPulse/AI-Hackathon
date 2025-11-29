import { useTranslation } from '@shared/i18n/hooks'
import { useTheme } from '@shared/theme'
import { FaSun, FaMoon } from 'react-icons/fa'
import './Header.css'

export const Header = () => {
  const { currentLanguage, changeLanguage } = useTranslation()
  const { theme, toggleTheme } = useTheme()
  
  return (
    <header className="header">
      <div className="header-content">
        <h1 className="header-title">
          AI Detection Monitor
        </h1>
        <div className="header-controls">
          <select
            value={currentLanguage}
            onChange={(e) => changeLanguage(e.target.value)}
            className="header-select"
          >
            <option value="en">EN</option>
            <option value="ru">RU</option>
          </select>
          <button
            onClick={toggleTheme}
            className="header-theme-button"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <FaMoon className="header-icon" />
            ) : (
              <FaSun className="header-icon" />
            )}
          </button>
        </div>
      </div>
    </header>
  )
}

