import React, { useState } from 'react'
import { useAuth } from 'react-oidc-context'
import './SignInView.css'

export default function SignInView() {
  const auth = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // Triggers the OIDC/Cognito Managed Login redirect flow
  const handleCognitoSignIn = () => {
    auth.signinRedirect()
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setErrorMessage(null)

    if (!email || !password) {
      setErrorMessage('Please enter both email and password.')
      return
    }

    setIsSubmitting(true)
    try {
      // Directs to Cognito authentication provider endpoint
      await auth.signinRedirect({
        extraQueryParams: { login_hint: email },
      })
    } catch (err: any) {
      setErrorMessage(err.message || 'An error occurred while signing in.')
      setIsSubmitting(false)
    }
  }

  return (
    <main className="openbox-signin-page">
      <div className="openbox-signin-container">
        {/* Brand Logo Header */}
        <a className="openbox-brand" href="/" aria-label="OpenBox home">
          OpenBox
        </a>

        <h1 className="openbox-signin-title">Sign in</h1>

        {errorMessage && (
          <div className="openbox-signin-error" role="alert">
            {errorMessage}
          </div>
        )}

        {/* Credentials Form */}
        <form className="openbox-signin-form" onSubmit={handleSubmit} noValidate>
          <div className="openbox-form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              className="openbox-input"
              placeholder="alex@acme.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="openbox-form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="openbox-input"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          <div className="openbox-signin-forgot">
            <button type="button" className="openbox-link-button" onClick={handleCognitoSignIn}>
              Forgot password?
            </button>
          </div>

          <button
            type="submit"
            className="openbox-button openbox-button--primary openbox-button--full"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <span className="openbox-spinner openbox-spinner--small" />
                Signing in…
              </>
            ) : (
              'Sign in'
            )}
          </button>
        </form>

        {/* Sign Up Redirect */}
        <footer className="openbox-signin-footer">
          <span>New to OpenBox?</span>
          <button
            type="button"
            className="openbox-link-button openbox-link-button--primary"
            onClick={handleCognitoSignIn}
          >
            Create an account
          </button>
        </footer>
      </div>
    </main>
  )
}
