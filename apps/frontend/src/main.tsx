import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { AuthProvider } from 'react-oidc-context'
import { cognitoAuthConfig } from './auth/config'
import HomeView from './views/HomeView'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider {...cognitoAuthConfig}>
      <HomeView />
    </AuthProvider>
  </StrictMode>,
)
