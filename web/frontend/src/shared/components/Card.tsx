import type { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  hover?: boolean
}

export const Card = ({ children, className = '', hover = false }: CardProps) => {
  const baseClasses = 'bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-6'
  const hoverClasses = hover ? 'transition-shadow hover:shadow-lg' : ''
  
  return (
    <div className={`${baseClasses} ${hoverClasses} ${className}`}>
      {children}
    </div>
  )
}

