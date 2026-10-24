import { useHealth } from '@/hooks/useHealth'
import { useAuth } from "react-oidc-context";
import { cognitoLogoutUrl } from '@/auth/config'

export default function HomeView() {
  const { health, error, loading } = useHealth()
  const auth = useAuth();

  const signOutRedirect = async () => {
    await auth.removeUser();
    if (cognitoLogoutUrl) window.location.href = cognitoLogoutUrl;
  };

  if (auth.isLoading) {
    return <div>Loading...</div>;
  }

  if (auth.error) {
    return <div>Encountering error... {auth.error.message}</div>;
  }

  if (auth.isAuthenticated) {
    return <div>DZiała logowanie:)</div>
  }

  return (
    <div>
      <button onClick={() => auth.signinRedirect()}>Sign in</button>
      <button onClick={() => signOutRedirect()}>Sign out</button>
    </div>
  );
}
