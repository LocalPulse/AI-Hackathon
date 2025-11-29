interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export const Spinner = ({ size = 'md', className = '' }: SpinnerProps) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }
  
  return (
    <div className={`inline-block ${className}`}>
      <div
        className={`${sizeClasses[size]} border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin dark:border-gray-700 dark:border-t-blue-500`}
      />
    </div>
  )
}

