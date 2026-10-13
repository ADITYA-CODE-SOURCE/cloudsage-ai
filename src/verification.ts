export type OriginalErrorStatus = 'present' | 'not observed' | 'inconclusive'
export type HealthResult = 'passed' | 'failed' | 'not checked'

export function compareIncident(originalQuotes: string[], freshLogs: string, health: HealthResult): { originalError: OriginalErrorStatus; applicationHealth: HealthResult } {
  if (!freshLogs.trim()) return { originalError: 'inconclusive', applicationHealth: health }
  const originalError = originalQuotes.some(quote => quote.length > 0 && freshLogs.includes(quote)) ? 'present' : 'not observed'
  return { originalError, applicationHealth: health }
}
