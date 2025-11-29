import type { ReactNode } from 'react'

interface TableProps {
  children: ReactNode
  className?: string
}

export const Table = ({ children, className = '' }: TableProps) => {
  return (
    <div className="overflow-x-auto">
      <table className={`min-w-full divide-y divide-gray-200 dark:divide-gray-700 ${className}`}>
        {children}
      </table>
    </div>
  )
}

interface TableHeadProps {
  children: ReactNode
}

export const TableHead = ({ children }: TableHeadProps) => {
  return (
    <thead className="bg-gray-50 dark:bg-gray-900">
      {children}
    </thead>
  )
}

interface TableBodyProps {
  children: ReactNode
}

export const TableBody = ({ children }: TableBodyProps) => {
  return (
    <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
      {children}
    </tbody>
  )
}

interface TableRowProps {
  children: ReactNode
  className?: string
}

export const TableRow = ({ children, className = '' }: TableRowProps) => {
  return (
    <tr className={className}>
      {children}
    </tr>
  )
}

interface TableCellProps {
  children: ReactNode
  className?: string
  header?: boolean
}

export const TableCell = ({ children, className = '', header = false }: TableCellProps) => {
  const baseClasses = header
    ? 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400'
    : 'px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100'
  
  const Component = header ? 'th' : 'td'
  
  return (
    <Component className={`${baseClasses} ${className}`}>
      {children}
    </Component>
  )
}

