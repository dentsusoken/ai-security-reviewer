/**
 * Resolve Toggle component for finding status management.
 *
 * Provides a button to toggle between open and resolved states.
 */
import { CheckCircle, Loader2, Undo2 } from 'lucide-react';
import type { ResolutionState } from '../../types/api';

interface ResolveToggleProps {
  /** Current resolution state */
  state: ResolutionState;
  /** Whether the toggle is loading */
  isLoading?: boolean;
  /** Toggle callback */
  onToggle: () => void;
  /** Whether to show compact view */
  compact?: boolean;
  /** Additional class names */
  className?: string;
}

/**
 * Toggle button for finding resolution state.
 */
export function ResolveToggle({
  state,
  isLoading = false,
  onToggle,
  compact = false,
  className = '',
}: ResolveToggleProps) {
  const isResolved = state === 'resolved';

  const baseStyles = compact
    ? 'px-2 py-1 rounded text-xs'
    : 'px-4 py-2 rounded-lg text-sm';

  const resolvedStyles = {
    background: 'var(--bg-elevated)',
    color: 'var(--text-secondary)',
    border: '1px solid var(--border)',
  };

  const openStyles = {
    background: 'rgba(22, 163, 74, 0.2)',
    color: '#16A34A',
    border: '1px solid rgba(22, 163, 74, 0.3)',
  };

  return (
    <button
      onClick={onToggle}
      disabled={isLoading}
      className={`${baseStyles} transition hover:opacity-80 inline-flex items-center gap-2 disabled:opacity-50 ${className}`}
      style={isResolved ? resolvedStyles : openStyles}
    >
      {isLoading ? (
        <Loader2 className={compact ? 'w-3 h-3 animate-spin' : 'w-4 h-4 animate-spin'} />
      ) : isResolved ? (
        <Undo2 className={compact ? 'w-3 h-3' : 'w-4 h-4'} />
      ) : (
        <CheckCircle className={compact ? 'w-3 h-3' : 'w-4 h-4'} />
      )}
      {isResolved ? '未対応に戻す' : '対応済みにする'}
    </button>
  );
}

/**
 * Resolution state badge for display.
 */
interface ResolutionBadgeProps {
  state: ResolutionState;
  className?: string;
}

export function ResolutionBadge({ state, className = '' }: ResolutionBadgeProps) {
  if (state !== 'resolved') {
    return null;
  }

  return (
    <div
      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-bold ${className}`}
      style={{
        background: 'rgba(22, 163, 74, 0.2)',
        color: '#16A34A',
        border: '1px solid rgba(22, 163, 74, 0.3)',
      }}
    >
      <CheckCircle className="w-3 h-3" />
      対応済み
    </div>
  );
}
