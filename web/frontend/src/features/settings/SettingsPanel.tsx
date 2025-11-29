import { Card } from '@shared/components'
import { useTranslation } from '@shared/i18n/hooks'
import { useTheme } from '@shared/theme'
import { Select } from '@shared/components'

export const SettingsPanel = () => {
  const { t, currentLanguage, changeLanguage } = useTranslation()
  const { theme, setTheme } = useTheme()
  
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        {t('settings.title')}
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {t('settings.language')}
          </h3>
          <Select
            value={currentLanguage}
            onChange={(e) => changeLanguage(e.target.value)}
            options={[
              { value: 'en', label: t('settings.english') },
              { value: 'ru', label: t('settings.russian') },
            ]}
          />
        </Card>
        
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {t('settings.theme')}
          </h3>
          <Select
            value={theme}
            onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}
            options={[
              { value: 'light', label: t('settings.light') },
              { value: 'dark', label: t('settings.dark') },
            ]}
          />
        </Card>
      </div>
    </div>
  )
}

