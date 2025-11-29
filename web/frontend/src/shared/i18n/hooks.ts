import { useTranslation as useI18nTranslation } from 'react-i18next'

export const useTranslation = () => {
  const { t, i18n } = useI18nTranslation()
  
  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng)
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem('language', lng)
      }
    } catch (error) {
      console.warn('Failed to save language to localStorage:', error)
    }
  }
  
  return { t, changeLanguage, currentLanguage: i18n.language }
}

