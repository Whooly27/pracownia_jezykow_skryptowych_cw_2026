import { useHealth } from '@/hooks/useHealth'
import { useAuth } from 'react-oidc-context'
import { cognitoLogoutUrl } from '@/auth/config'
import { useNavigate } from 'react-router'
import './HomeView.css'

function ShareIllustration() {
  return (
    <div
      className="openbox-illustration"
      aria-label="Illustration of a file shared with selected people"
    >
      <svg
        className="openbox-illustration__art"
        viewBox="0 0 440 340"
        role="img"
        aria-labelledby="share-art-title"
      >
        <title id="share-art-title">A document shared securely with three people</title>
        <circle cx="220" cy="170" r="145" fill="#eff5ff" />
        <circle cx="57" cy="54" r="3" fill="#9fc5ff" />
        <circle cx="379" cy="239" r="4" fill="#9fc5ff" />
        <path
          d="M102 94 L174 132 M335 91 L269 130 M323 267 L268 224"
          stroke="#78adff"
          strokeWidth="2.5"
          strokeDasharray="5 7"
          fill="none"
        />
        <g transform="translate(155 91) rotate(-5 67 90)">
          <rect
            x="0"
            y="0"
            width="137"
            height="184"
            rx="13"
            fill="#fff"
            stroke="#7eafff"
            strokeWidth="2.5"
          />
          <path d="M0 36 H137" stroke="#d8e7ff" strokeWidth="2" />
          <text x="17" y="24" fontSize="12" fontWeight="700" fill="#2869d9">
            XLS
          </text>
          <rect x="19" y="57" width="99" height="10" rx="5" fill="#c6dcff" />
          <rect x="19" y="82" width="77" height="10" rx="5" fill="#c6dcff" />
          <rect x="19" y="107" width="91" height="10" rx="5" fill="#c6dcff" />
          <rect x="19" y="132" width="63" height="10" rx="5" fill="#c6dcff" />
        </g>
        {[
          { x: 77, y: 83, initials: 'KA' },
          { x: 353, y: 79, initials: 'JO' },
          { x: 326, y: 271, initials: 'DA' },
        ].map((person) => (
          <g key={person.initials}>
            <circle
              cx={person.x}
              cy={person.y}
              r="28"
              fill="#fff"
              stroke="#78adff"
              strokeWidth="2.5"
            />
            <text
              x={person.x}
              y={person.y + 6}
              textAnchor="middle"
              fontSize="17"
              fontWeight="700"
              fill="#1763d5"
            >
              {person.initials}
            </text>
          </g>
        ))}
        <g transform="translate(20 250)">
          <rect width="112" height="39" rx="19.5" fill="#fff" stroke="#78adff" strokeWidth="2" />
          <path
            d="M26 19a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.72"
            fill="none"
            stroke="#1763d5"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M30 17a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.72-1.72"
            fill="none"
            stroke="#1763d5"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <text x="48" y="24" fontSize="13" fontWeight="700" fill="#243044">
            Dec 24
          </text>
        </g>
        <path d="M365 34l4 9 9 4-9 4-4 9-4-9-9-4 9-4z" fill="#ffc94d" />
        <path d="M116 302l3 7 7 3-7 3-3 7-3-7-7-3 7-3z" fill="#8bbaff" />
        <path d="M302 315l3 7 7 3-7 3-3 7-3-7-7-3 7-3z" fill="#8bbaff" />
      </svg>
    </div>
  )
}

export default function HomeView() {
  const { health, error: healthError, loading } = useHealth()
  const auth = useAuth()
  const navigate = useNavigate()

  const signOutRedirect = async () => {
    await auth.removeUser()
    if (cognitoLogoutUrl) window.location.href = cognitoLogoutUrl
  }

  const goToSignIn = () => {
    navigate('/signin')
  }

  if (auth.isLoading) {
    return (
      <main className="openbox-status" aria-live="polite">
        <span className="openbox-spinner" />
        <span>Loading OpenBox…</span>
      </main>
    )
  }

  if (auth.error) {
    return (
      <main className="openbox-status openbox-status--error" role="alert">
        <strong>We couldn’t connect to OpenBox.</strong>
        <span>{auth.error?.message}</span>
        <button
          className="openbox-button openbox-button--primary"
          onClick={() => window.location.reload()}
        >
          Try again
        </button>
      </main>
    )
  }

  if (auth.isAuthenticated) {
    return (
      <main className="openbox-status">
        <strong>You’re signed in to OpenBox.</strong>
        <span>Continue to your files to get started.</span>
        <div style={{ display: 'flex', gap: '12px', marginTop: '10px' }}>
          <a className="openbox-button openbox-button--primary" href="/files">
            Go to files
          </a>
          <button className="openbox-button openbox-button--quiet" onClick={signOutRedirect}>
            Sign out
          </button>
        </div>
      </main>
    )
  }

  return (
    <main className="openbox-page">
      <div className="openbox-browser">
        <header className="openbox-header">
          <a className="openbox-brand" href="/" aria-label="OpenBox home">
            OpenBox
          </a>
          <nav className="openbox-header__actions" aria-label="Account">
            <button className="openbox-button openbox-button--quiet" onClick={goToSignIn}>
              Sign in
            </button>
            <button className="openbox-button openbox-button--primary" onClick={goToSignIn}>
              Create account
            </button>
          </nav>
        </header>

        <section className="openbox-hero" aria-labelledby="openbox-heading">
          <div className="openbox-hero__copy">
            <h1 id="openbox-heading">Share files with exactly the people who need them</h1>
            <p>
              Upload files, share one file at a time with the right permissions, and send links that
              expire.
            </p>
            <div className="openbox-hero__actions">
              <button className="openbox-button openbox-button--primary" onClick={goToSignIn}>
                Create account
              </button>
              <button className="openbox-button openbox-button--quiet" onClick={goToSignIn}>
                Sign in
              </button>
            </div>
          </div>
          <ShareIllustration />
        </section>
      </div>

      <nav className="openbox-mobile-actions" aria-label="Account">
        <button className="openbox-button openbox-button--quiet" onClick={goToSignIn}>
          Sign in
        </button>
        <button className="openbox-button openbox-button--primary" onClick={goToSignIn}>
          Create account
        </button>
      </nav>
    </main>
  )
}
