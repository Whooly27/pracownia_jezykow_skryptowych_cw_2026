import { describe, it, expect, vi, afterEach } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'

import HomeView from '@/views/HomeView'

describe('HomeView', () => {
  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it('renders backend health status', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockResolvedValue(
          new Response(JSON.stringify({ status: 'ok', database: 'ok' }), { status: 200 }),
        ),
    )

    render(<HomeView />)

    const status = await screen.findByText(/Backend:/)
    expect(status.textContent).toContain('Backend: ok')
    expect(status.textContent).toContain('Database: ok')
  })

  it('shows an alert when the backend is unreachable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 503 })))

    render(<HomeView />)

    expect((await screen.findByRole('alert')).textContent).toContain('503')
  })
})
