/**
 * Authentication module exports.
 */
export { AuthProvider, AuthenticatedTemplate, UnauthenticatedTemplate } from './AuthProvider';
export { AuthContext, useAuth, useUser, useIsLoggedIn } from './AuthContext';
export type { AuthContextValue, User } from './AuthContext';
export { ProtectedRoute, PublicOnlyRoute, withAuth } from './ProtectedRoute';
export { msalConfig, loginRequest, apiRequest, isMsalConfigured } from './msalConfig';
