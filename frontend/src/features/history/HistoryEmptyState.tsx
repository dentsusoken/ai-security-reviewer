/**
 * History empty state component.
 *
 * Displays appropriate message when history list is empty, with context-aware
 * messaging based on whether filters are applied.
 */
import { FileSearch, History, PlusCircle, XCircle } from 'lucide-react';
import React from 'react';

/**
 * Props for HistoryEmptyState.
 */
export interface HistoryEmptyStateProps {
  /** Whether filters are currently applied */
  hasFilters: boolean;
  /** Callback to clear all filters */
  onClearFilters?: () => void;
  /** Callback to start a new review */
  onStartNewReview?: () => void;
}

/**
 * Empty state display for history page.
 *
 * Shows different messages depending on context:
 * - No reviews yet: encourage starting first review
 * - No matching results: suggest clearing filters
 *
 * @example
 * ```tsx
 * <HistoryEmptyState
 *   hasFilters={hasActiveFilters}
 *   onClearFilters={clearFilters}
 *   onStartNewReview={() => navigate('/review/new')}
 * />
 * ```
 */
export function HistoryEmptyState({
  hasFilters,
  onClearFilters,
  onStartNewReview,
}: HistoryEmptyStateProps): React.ReactElement {
  if (hasFilters) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4">
        <div className="p-4 bg-amber-100 dark:bg-amber-900/30 rounded-full mb-4">
          <FileSearch className="w-8 h-8 text-amber-600 dark:text-amber-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          該当するレビューがありません
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-center max-w-sm mb-6">
          現在のフィルター条件に一致するレビュー履歴が見つかりませんでした。
          条件を変更するか、すべてのフィルターをクリアしてください。
        </p>
        {onClearFilters && (
          <button
            onClick={onClearFilters}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium
              text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-900/20
              border border-amber-200 dark:border-amber-700 rounded-lg
              hover:bg-amber-100 dark:hover:bg-amber-900/40
              transition-colors duration-200"
          >
            <XCircle className="w-4 h-4" />
            フィルターをクリア
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
        <History className="w-8 h-8 text-gray-400 dark:text-gray-500" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
        まだレビュー履歴がありません
      </h3>
      <p className="text-gray-500 dark:text-gray-400 text-center max-w-sm mb-6">
        セキュリティレビューを実行すると、その結果がここに表示されます。
        最初のレビューを開始してみましょう。
      </p>
      {onStartNewReview && (
        <button
          onClick={onStartNewReview}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium
            text-white bg-blue-600 rounded-lg
            hover:bg-blue-700 active:bg-blue-800
            transition-colors duration-200"
        >
          <PlusCircle className="w-4 h-4" />
          新規レビューを開始
        </button>
      )}
    </div>
  );
}

/**
 * Skeleton loader for history list.
 */
export function HistoryListSkeleton(): React.ReactElement {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 animate-pulse"
        >
          <div className="flex items-start gap-4">
            {/* Score circle skeleton */}
            <div className="w-12 h-12 rounded-full bg-gray-200 dark:bg-gray-700" />

            <div className="flex-1 space-y-2">
              {/* Title skeleton */}
              <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
              {/* Subtitle skeleton */}
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
              {/* Badges skeleton */}
              <div className="flex gap-2 mt-2">
                <div className="h-6 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
                <div className="h-6 w-20 bg-gray-200 dark:bg-gray-700 rounded" />
              </div>
            </div>

            {/* Arrow/action skeleton */}
            <div className="w-6 h-6 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Loading state component for history page.
 */
export function HistoryLoadingState(): React.ReactElement {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="flex justify-between items-center">
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-32 animate-pulse" />
        <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded w-24 animate-pulse" />
      </div>

      {/* Filters skeleton */}
      <div className="flex gap-4">
        <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded flex-1 max-w-xs animate-pulse" />
        <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded w-32 animate-pulse" />
        <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded w-32 animate-pulse" />
      </div>

      {/* List skeleton */}
      <HistoryListSkeleton />
    </div>
  );
}

/**
 * Error state component for history page.
 */
export interface HistoryErrorStateProps {
  /** Error message to display */
  message: string;
  /** Callback to retry loading */
  onRetry?: () => void;
}

export function HistoryErrorState({
  message,
  onRetry,
}: HistoryErrorStateProps): React.ReactElement {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="p-4 bg-red-100 dark:bg-red-900/30 rounded-full mb-4">
        <XCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
        エラーが発生しました
      </h3>
      <p className="text-gray-500 dark:text-gray-400 text-center max-w-sm mb-6">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium
            text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-900/20
            border border-blue-200 dark:border-blue-700 rounded-lg
            hover:bg-blue-100 dark:hover:bg-blue-900/40
            transition-colors duration-200"
        >
          再試行
        </button>
      )}
    </div>
  );
}
