/**
 * Protected route component for authentication guards.
 *
 * Redirects unauthenticated users to the landing page or login.
 */
import { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

interface ProtectedRouteProps {
  /** Child components to render when authenticated */
  children: ReactNode;
  /** Path to redirect to when not authenticated (default: /) */
  redirectTo?: string;
  /** Whether to show a loading state while checking auth */
  showLoading?: boolean;
}

/**
 * Loading spinner component.
 */
function LoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400">認証状態を確認中...</p>
      </div>
    </div>
  );
}

/**
 * Protected route wrapper that requires authentication.
 *
 * Usage:
 * ```tsx
 * <Route
 *   path="/dashboard"
 *   element={
 *     <ProtectedRoute>
 *       <DashboardPage />
 *     </ProtectedRoute>
 *   }
 * />
 * ```
 */
export function ProtectedRoute({
  children,
  redirectTo = '/',
  showLoading = true,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  // Show loading state while checking auth
  if (isLoading && showLoading) {
    return <LoadingSpinner />;
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    // Save the attempted URL for redirecting after login
    return (
      <Navigate
        to={redirectTo}
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  // Render protected content
  return <>{children}</>;
}

/**
 * Higher-order component to wrap a component with authentication guard.
 */
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  redirectTo = '/'
) {
  return function AuthenticatedComponent(props: P) {
    return (
      <ProtectedRoute redirectTo={redirectTo}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}

/**
 * Route that only renders for unauthenticated users.
 *
 * Redirects authenticated users to the dashboard.
 */
interface PublicOnlyRouteProps {
  children: ReactNode;
  redirectTo?: string;
}

export function PublicOnlyRoute({
  children,
  redirectTo = '/dashboard',
}: PublicOnlyRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  // Show loading state while checking auth
  if (isLoading) {
    return <LoadingSpinner />;
  }

  // Redirect authenticated users to dashboard
  if (isAuthenticated) {
    // Check if there's a saved location to redirect to
    const from = (location.state as { from?: string })?.from || redirectTo;
    return <Navigate to={from} replace />;
  }

  // Render public content
  return <>{children}</>;
}
