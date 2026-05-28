/**
 * History data fetching and filtering hook.
 *
 * Provides history data with filtering, search, and pagination support.
 */
import { useCallback, useEffect, useState } from 'react';
import { historyApi } from '../../services/api';
import type { HistoryReview } from '../../types/api';

/**
 * History filter options.
 */
export interface HistoryFilters {
  /** Search query for repo name */
  query?: string;
  /** Time period filter */
  period?: 'today' | 'week' | 'month' | 'quarter' | null;
  /** Score range filter */
  scoreRange?: '0-50' | '51-70' | '71-85' | '86-100' | null;
  /** Perspective filter */
  perspective?: string | null;
}

/**
 * History state returned by the hook.
 */
export interface HistoryState {
  /** List of reviews */
  reviews: HistoryReview[];
  /** Total count of reviews matching filters */
  totalCount: number;
  /** Loading state */
  loading: boolean;
  /** Error message if any */
  error: string | null;
  /** Current filters */
  filters: HistoryFilters;
  /** Update filters */
  setFilters: (filters: Partial<HistoryFilters>) => void;
  /** Clear all filters */
  clearFilters: () => void;
  /** Refresh data */
  refresh: () => Promise<void>;
  /** Whether any filters are active */
  hasActiveFilters: boolean;
}

const DEFAULT_FILTERS: HistoryFilters = {
  query: '',
  period: null,
  scoreRange: null,
  perspective: null,
};

/**
 * Hook for fetching and filtering review history.
 *
 * @param options - Optional configuration
 * @returns History state with data, filters, and actions
 *
 * @example
 * ```tsx
 * const { reviews, filters, setFilters, loading, hasActiveFilters, clearFilters } = useHistory();
 *
 * // Apply search filter
 * setFilters({ query: 'myrepo' });
 *
 * // Apply period filter
 * setFilters({ period: 'week' });
 *
 * // Clear all filters
 * clearFilters();
 * ```
 */
export function useHistory(options?: {
  /** Auto-fetch on mount (default: true) */
  autoFetch?: boolean;
  /** Initial filters */
  initialFilters?: HistoryFilters;
}): HistoryState {
  const { autoFetch = true, initialFilters } = options || {};

  const [reviews, setReviews] = useState<HistoryReview[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFiltersState] = useState<HistoryFilters>({
    ...DEFAULT_FILTERS,
    ...initialFilters,
  });

  // Check if any filters are active
  const hasActiveFilters =
    !!filters.query || !!filters.period || !!filters.scoreRange || !!filters.perspective;

  // Fetch history with current filters
  const fetchHistory = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await historyApi.list({
        query: filters.query || undefined,
        period: filters.period || undefined,
        scoreRange: filters.scoreRange || undefined,
        perspective: filters.perspective || undefined,
      });

      setReviews(data.reviews);
      setTotalCount(data.totalCount);
    } catch (err) {
      console.error('Failed to fetch history:', err);
      setError('履歴の読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Auto-fetch on mount and when filters change
  useEffect(() => {
    if (autoFetch) {
      fetchHistory();
    }
  }, [autoFetch, fetchHistory]);

  // Update filters
  const setFilters = useCallback((newFilters: Partial<HistoryFilters>) => {
    setFiltersState((prev) => ({
      ...prev,
      ...newFilters,
    }));
  }, []);

  // Clear all filters
  const clearFilters = useCallback(() => {
    setFiltersState(DEFAULT_FILTERS);
  }, []);

  return {
    reviews,
    totalCount,
    loading,
    error,
    filters,
    setFilters,
    clearFilters,
    refresh: fetchHistory,
    hasActiveFilters,
  };
}

/**
 * Format duration in milliseconds to human-readable string.
 */
export function formatDuration(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${minutes}分${seconds}秒`;
}

/**
 * Format ISO timestamp to localized string.
 */
export function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format relative time (e.g., "3日前").
 */
export function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMinutes < 1) {
    return 'たった今';
  } else if (diffMinutes < 60) {
    return `${diffMinutes}分前`;
  } else if (diffHours < 24) {
    return `${diffHours}時間前`;
  } else if (diffDays < 7) {
    return `${diffDays}日前`;
  } else {
    return formatTimestamp(isoString);
  }
}

/**
 * Get color for score.
 */
export function getScoreColor(score: number): string {
  if (score >= 85) return '#16A34A';
  if (score >= 70) return '#CA8A04';
  if (score >= 50) return '#EA580C';
  return '#E11D48';
}

/**
 * Get score grade.
 */
export function getScoreGrade(score: number): string {
  if (score >= 90) return 'A';
  if (score >= 80) return 'B';
  if (score >= 70) return 'C';
  if (score >= 60) return 'D';
  return 'F';
}
