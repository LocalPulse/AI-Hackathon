import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import enTranslations from './locales/en/translations.json'
import ruTranslations from './locales/ru/translations.json'

const getStoredLanguage = (): string => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      return localStorage.getItem('language') || 'en'
    }
  } catch {
    // localStorage is not available
  }
  return 'en'
}

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: enTranslations },
      ru: { translation: ruTranslations },
    },
    lng: getStoredLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  })

export default i18n

