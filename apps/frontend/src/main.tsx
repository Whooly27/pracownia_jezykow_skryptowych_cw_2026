import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { AuthProvider } from 'react-oidc-context'
import { RouterProvider } from 'react-router/dom'

import { cognitoAuthConfig } from './auth/config'
import { router } from './router'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider {...cognitoAuthConfig}>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>,
)
