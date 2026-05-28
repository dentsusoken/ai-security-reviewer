/**
 * Dashboard data fetching and state management hook.
 *
 * Provides dashboard statistics and recent reviews with
 * loading states and error handling.
 */
import { useCallback, useEffect, useState } from 'react';
import { dashboardApi } from '../../services/api';
import type { DashboardStats, HistoryReview } from '../../types/api';

/**
 * Dashboard state returned by the hook.
 */
export interface DashboardState {
  /** Dashboard statistics */
  stats: {
    totalReviews: number;
    totalFindings: number;
    resolvedFindings: number;
    averageScore: number;
  } | null;
  /** Recent reviews list */
  recentReviews: HistoryReview[];
  /** Loading state */
  loading: boolean;
  /** Error message if any */
  error: string | null;
  /** Refresh dashboard data */
  refresh: () => Promise<void>;
}

/**
 * Hook for fetching and managing dashboard data.
 *
 * @param options - Optional configuration
 * @returns Dashboard state with data and actions
 *
 * @example
 * ```tsx
 * const { stats, recentReviews, loading, error, refresh } = useDashboard();
 *
 * if (loading) return <Spinner />;
 * if (error) return <Error message={error} />;
 *
 * return <Dashboard stats={stats} reviews={recentReviews} />;
 * ```
 */
export function useDashboard(options?: {
  /** Auto-fetch on mount (default: true) */
  autoFetch?: boolean;
  /** Refresh interval in milliseconds (default: none) */
  refreshInterval?: number;
}): DashboardState {
  const { autoFetch = true, refreshInterval } = options || {};

  const [stats, setStats] = useState<DashboardState['stats']>(null);
  const [recentReviews, setRecentReviews] = useState<HistoryReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data: DashboardStats = await dashboardApi.getStats();

      setStats({
        totalReviews: data.totalReviews,
        totalFindings: data.totalFindings,
        resolvedFindings: data.resolvedFindings,
        averageScore: data.averageScore,
      });

      setRecentReviews(data.recentReviews || []);
    } catch (err) {
      console.error('Failed to fetch dashboard stats:', err);
      setError('ダッシュボードの読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-fetch on mount
  useEffect(() => {
    if (autoFetch) {
      fetchDashboard();
    }
  }, [autoFetch, fetchDashboard]);

  // Refresh interval
  useEffect(() => {
    if (!refreshInterval) return;

    const intervalId = setInterval(fetchDashboard, refreshInterval);
    return () => clearInterval(intervalId);
  }, [refreshInterval, fetchDashboard]);

  return {
    stats,
    recentReviews,
    loading,
    error,
    refresh: fetchDashboard,
  };
}

/**
 * Helper to format duration in milliseconds to human-readable string.
 */
export function formatDuration(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${minutes}分${seconds}秒`;
}

/**
 * Helper to format ISO timestamp to localized string.
 */
export function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString('ja-JP', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Helper to extract repository name from URL.
 */
export function getRepoName(url: string): string {
  const parts = url.split('/');
  return parts[parts.length - 1] || url;
}

/**
 * Helper to get owner/repo format from GitHub URL.
 */
export function getOwnerRepo(url: string): string {
  try {
    const match = url.match(/github\.com\/([^/]+\/[^/]+)/);
    return match ? match[1] : url;
  } catch {
    return url;
  }
}
