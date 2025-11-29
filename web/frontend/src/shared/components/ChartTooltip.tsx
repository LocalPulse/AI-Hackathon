import type { TooltipProps } from 'recharts'

interface ChartTooltipProps extends TooltipProps<number, string> {
  labelFormatter?: (label: string | number) => string
  valueFormatter?: (value: number) => string
  unit?: string
  nameFormatter?: (name: string) => string
}

export const ChartTooltip = ({ 
  active, 
  payload, 
  label,
  labelFormatter,
  valueFormatter,
  unit = '',
  nameFormatter
}: ChartTooltipProps) => {
  if (active && payload && payload.length) {
    const formattedLabel = labelFormatter ? labelFormatter(label as string) : String(label)
    
    return (
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-3">
        <p className="text-gray-600 dark:text-white font-medium mb-1">{formattedLabel}</p>
        {payload.map((entry, index) => {
          const value = entry.value as number
          const formatted = valueFormatter ? valueFormatter(value) : value.toFixed(2)
          const color = entry.color || '#3b82f6'
          const displayName = nameFormatter && entry.name ? nameFormatter(entry.name) : (entry.name || 'value')
          
          return (
            <p key={index} style={{ color }} className="dark:text-blue-400">
              <span className="text-gray-700 dark:text-gray-300">{displayName}: </span>
              {formatted}{unit}
            </p>
          )
        })}
      </div>
    )
  }
  return null
}

