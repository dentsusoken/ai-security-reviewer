/**
 * MSAL Authentication Provider for Azure Entra ID.
 *
 * This provider wraps the application with MSAL authentication context
 * and provides login/logout functionality.
 */
import { ReactNode, useCallback, useEffect, useState } from 'react';
import {
  MsalProvider,
  useMsal,
  useIsAuthenticated,
  AuthenticatedTemplate,
  UnauthenticatedTemplate,
} from '@azure/msal-react';
import {
  PublicClientApplication,
  EventType,
  AccountInfo,
  InteractionStatus,
} from '@azure/msal-browser';
import { msalConfig, loginRequest, isMsalConfigured } from './msalConfig';
import { AuthContext, AuthContextValue, User } from './AuthContext';

// Create MSAL instance
const msalInstance = new PublicClientApplication(msalConfig);

// Initialize MSAL instance
msalInstance.initialize().then(() => {
  // Handle redirect response
  msalInstance.handleRedirectPromise().catch((error) => {
    console.error('Redirect error:', error);
  });

  // Set active account on login success
  msalInstance.addEventCallback((event) => {
    if (event.eventType === EventType.LOGIN_SUCCESS && event.payload) {
      const payload = event.payload as { account: AccountInfo };
      msalInstance.setActiveAccount(payload.account);
    }
  });

  // Set active account if available
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length > 0) {
    msalInstance.setActiveAccount(accounts[0]);
  }
});

/**
 * Convert MSAL AccountInfo to our User type.
 */
function accountToUser(account: AccountInfo | null): User | null {
  if (!account) {
    return null;
  }

  return {
    id: account.localAccountId,
    email: account.username,
    name: account.name || account.username,
    tenantId: account.tenantId,
  };
}

/**
 * Inner auth provider that uses MSAL hooks.
 */
function AuthProviderInner({ children }: { children: ReactNode }) {
  const { instance, accounts, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Update user when accounts change
  useEffect(() => {
    if (inProgress === InteractionStatus.None) {
      const activeAccount = instance.getActiveAccount();
      setUser(accountToUser(activeAccount));
      setIsLoading(false);
    }
  }, [instance, accounts, inProgress]);

  // Login function
  const login = useCallback(async () => {
    setError(null);
    try {
      await instance.loginPopup(loginRequest);
      const activeAccount = instance.getActiveAccount();
      setUser(accountToUser(activeAccount));
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      console.error('Login failed:', error);
      throw error;
    }
  }, [instance]);

  // Login with redirect
  const loginRedirect = useCallback(async () => {
    setError(null);
    try {
      await instance.loginRedirect(loginRequest);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      console.error('Login redirect failed:', error);
      throw error;
    }
  }, [instance]);

  // Logout function
  const logout = useCallback(async () => {
    setError(null);
    try {
      await instance.logoutPopup({
        postLogoutRedirectUri: window.location.origin,
      });
      setUser(null);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      console.error('Logout failed:', error);
      throw error;
    }
  }, [instance]);

  // Get access token
  const getAccessToken = useCallback(async (): Promise<string | null> => {
    const activeAccount = instance.getActiveAccount();
    if (!activeAccount) {
      return null;
    }

    try {
      const response = await instance.acquireTokenSilent({
        ...loginRequest,
        account: activeAccount,
      });
      return response.accessToken;
    } catch (err) {
      console.error('Token acquisition failed:', err);
      // Try interactive login if silent fails
      try {
        const response = await instance.acquireTokenPopup(loginRequest);
        return response.accessToken;
      } catch (popupErr) {
        console.error('Interactive token acquisition failed:', popupErr);
        return null;
      }
    }
  }, [instance]);

  const contextValue: AuthContextValue = {
    user,
    isAuthenticated,
    isLoading: isLoading || inProgress !== InteractionStatus.None,
    error,
    login,
    loginRedirect,
    logout,
    getAccessToken,
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
}

/**
 * Development mode provider (no MSAL).
 */
function DevAuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  const login = useCallback(async () => {
    // Simulate login in dev mode
    setUser({
      id: 'dev-user-001',
      email: 'dev@example.com',
      name: '開発ユーザー',
      tenantId: 'dev-tenant',
    });
    setIsAuthenticated(true);
  }, []);

  const logout = useCallback(async () => {
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const getAccessToken = useCallback(async () => {
    return 'dev-token';
  }, []);

  const contextValue: AuthContextValue = {
    user,
    isAuthenticated,
    isLoading: false,
    error: null,
    login,
    loginRedirect: login,
    logout,
    getAccessToken,
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
}

/**
 * Main AuthProvider component.
 *
 * Uses MSAL when configured, falls back to dev mode otherwise.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  // Check if MSAL is configured
  if (!isMsalConfigured()) {
    console.warn('MSAL not configured. Using development authentication mode.');
    return <DevAuthProvider>{children}</DevAuthProvider>;
  }

  return (
    <MsalProvider instance={msalInstance}>
      <AuthProviderInner>{children}</AuthProviderInner>
    </MsalProvider>
  );
}

// Re-export templates for convenience
export { AuthenticatedTemplate, UnauthenticatedTemplate };
