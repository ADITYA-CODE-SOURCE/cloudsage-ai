import { describe, expect, it } from 'vitest'
import { compareIncident } from './verification'

describe('before/after comparison', () => {
  it('does not equate an unobserved error with healthy application status', () => {
    expect(compareIncident(['connection refused'], 'Started successfully', 'not checked')).toEqual({
      originalError: 'not observed',
      applicationHealth: 'not checked',
    })
  })

  it('reports the original exact signature independently of manually reported health', () => {
    expect(compareIncident(['FATAL: database missing'], 'FATAL: database missing', 'passed')).toEqual({
      originalError: 'present',
      applicationHealth: 'passed',
    })
  })

  it('marks empty new logs as inconclusive', () => {
    expect(compareIncident(['original error'], '', 'failed')).toEqual({ originalError: 'inconclusive', applicationHealth: 'failed' })
  })
})
