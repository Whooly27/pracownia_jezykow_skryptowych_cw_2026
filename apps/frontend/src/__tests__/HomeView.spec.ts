import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

import HomeView from '@/views/HomeView.vue'

describe('HomeView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  afterEach(() => {
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

    const wrapper = mount(HomeView)
    await flushPromises()

    expect(wrapper.text()).toContain('Backend: ok')
    expect(wrapper.text()).toContain('Database: ok')
  })

  it('shows an alert when the backend is unreachable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 503 })))

    const wrapper = mount(HomeView)
    await flushPromises()

    expect(wrapper.find('[role="alert"]').text()).toContain('503')
  })
})
