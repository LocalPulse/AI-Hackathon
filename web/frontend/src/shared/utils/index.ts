export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

export const formatConfidence = (confidence: number): string => {
  return `${(confidence * 100).toFixed(1)}%`
}

export const debounce = <T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: number | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = window.setTimeout(() => func(...args), wait)
  }
}

