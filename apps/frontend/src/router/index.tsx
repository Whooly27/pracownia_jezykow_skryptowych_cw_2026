import { createBrowserRouter } from 'react-router'
import HomeView from '@/views/HomeView'
import SignInView from '@/views/SignInView'
import FilesView from '@/views/FilesView'
import FilesViewMock from '@/views/FilesViewMock'

export const router = createBrowserRouter(
  [
    { path: '/', element: <HomeView /> },
    { path: '/signin', element: <SignInView /> },
    { path: '/files', element: <FilesView /> },
    { path: '/files-mock', element: <FilesViewMock /> },
  ],
  {
    basename: import.meta.env.BASE_URL,
  },
)
