import { create } from 'zustand'

interface SettingsStore {
  language: string
  theme: 'light' | 'dark'
  setLanguage: (language: string) => void
  setTheme: (theme: 'light' | 'dark') => void
}

export const useSettingsStore = create<SettingsStore>((set) => ({
  language: localStorage.getItem('language') || 'en',
  theme: (localStorage.getItem('theme') as 'light' | 'dark') || 'light',
  setLanguage: (language) => {
    localStorage.setItem('language', language)
    set({ language })
  },
  setTheme: (theme) => {
    localStorage.setItem('theme', theme)
    set({ theme })
  },
}))

