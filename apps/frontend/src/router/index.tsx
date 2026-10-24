import { createBrowserRouter } from 'react-router'

import HomeView from '@/views/HomeView'

export const router = createBrowserRouter([{ path: '/', element: <HomeView /> }], {
  basename: import.meta.env.BASE_URL,
})
