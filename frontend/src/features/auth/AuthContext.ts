/**
 * Authentication context and hooks for accessing auth state.
 */
import { createContext, useContext } from 'react';

/**
 * User information from authentication.
 */
export interface User {
  id: string;
  email: string;
  name: string;
  tenantId?: string;
}

/**
 * Authentication context value.
 */
export interface AuthContextValue {
  /** Current authenticated user, or null if not authenticated */
  user: User | null;
  /** Whether the user is authenticated */
  isAuthenticated: boolean;
  /** Whether authentication state is being loaded */
  isLoading: boolean;
  /** Any authentication error */
  error: Error | null;
  /** Login using popup */
  login: () => Promise<void>;
  /** Login using redirect */
  loginRedirect: () => Promise<void>;
  /** Logout */
  logout: () => Promise<void>;
  /** Get access token for API calls */
  getAccessToken: () => Promise<string | null>;
}

/**
 * Authentication context.
 */
export const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Hook to access authentication context.
 *
 * @throws Error if used outside of AuthProvider
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * Hook to get the current user.
 *
 * @returns The current user or null
 */
export function useUser(): User | null {
  const { user } = useAuth();
  return user;
}

/**
 * Hook to check if the user is authenticated.
 *
 * @returns True if authenticated
 */
export function useIsLoggedIn(): boolean {
  const { isAuthenticated, isLoading } = useAuth();
  return !isLoading && isAuthenticated;
}
