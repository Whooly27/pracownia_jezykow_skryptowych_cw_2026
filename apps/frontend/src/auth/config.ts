import type { AuthProviderProps } from 'react-oidc-context'

const env = import.meta.env

export const cognitoAuthConfig: AuthProviderProps = {
  authority: env.VITE_OIDC_AUTHORITY,
  client_id: env.VITE_OIDC_CLIENT_ID,
  redirect_uri: env.VITE_OIDC_REDIRECT_URI ?? window.location.origin,
  response_type: 'code',
  scope: 'phone openid email',
  onSigninCallback: () => {
    window.history.replaceState({}, document.title, window.location.pathname)
  },
}

export const cognitoLogoutUrl: string | null = env.VITE_COGNITO_DOMAIN
  ? `${env.VITE_COGNITO_DOMAIN}/logout?${new URLSearchParams({
      client_id: env.VITE_OIDC_CLIENT_ID,
      logout_uri: env.VITE_OIDC_LOGOUT_URI ?? window.location.origin,
    })}`
  : null
