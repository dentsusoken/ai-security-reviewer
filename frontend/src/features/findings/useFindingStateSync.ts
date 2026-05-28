/**
 * Finding state synchronization hook.
 *
 * Manages finding resolution states and syncs updates across
 * the UI without requiring a full page reload.
 */
import { useCallback, useState } from 'react';
import { findingsApi } from '../../services/api';
import type { ResolutionState, FindingDetail, FindingSummary } from '../../types/api';

/**
 * Finding state entry.
 */
interface FindingStateEntry {
  id: string;
  resolutionState: ResolutionState;
  updatedAt: Date;
}

/**
 * Finding state sync result.
 */
export interface FindingStateSyncResult {
  /** Map of finding ID to resolution state */
  states: Map<string, ResolutionState>;
  /** Check if a finding is resolved */
  isResolved: (findingId: string) => boolean;
  /** Get resolution state for a finding */
  getState: (findingId: string) => ResolutionState;
  /** Toggle finding resolution state */
  toggleResolution: (findingId: string) => Promise<void>;
  /** Update finding state from detail fetch */
  updateFromDetail: (finding: FindingDetail) => void;
  /** Update multiple states from summary list */
  updateFromSummaries: (findings: FindingSummary[]) => void;
  /** Whether any update is in progress */
  isUpdating: boolean;
  /** ID of finding currently being updated */
  updatingId: string | null;
  /** Last error if any */
  error: string | null;
}

/**
 * Hook to manage and synchronize finding resolution states.
 *
 * @example
 * ```tsx
 * const { isResolved, toggleResolution, isUpdating } = useFindingStateSync();
 *
 * // Check if finding is resolved
 * if (isResolved(findingId)) { ... }
 *
 * // Toggle resolution state
 * await toggleResolution(findingId);
 * ```
 */
export function useFindingStateSync(): FindingStateSyncResult {
  const [states, setStates] = useState<Map<string, FindingStateEntry>>(new Map());
  const [isUpdating, setIsUpdating] = useState(false);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Get state map for external use
  const statesMap = new Map<string, ResolutionState>();
  states.forEach((entry, id) => {
    statesMap.set(id, entry.resolutionState);
  });

  // Check if a finding is resolved
  const isResolved = useCallback(
    (findingId: string): boolean => {
      const entry = states.get(findingId);
      return entry?.resolutionState === 'resolved';
    },
    [states]
  );

  // Get resolution state for a finding
  const getState = useCallback(
    (findingId: string): ResolutionState => {
      const entry = states.get(findingId);
      return entry?.resolutionState || 'open';
    },
    [states]
  );

  // Toggle finding resolution state
  const toggleResolution = useCallback(
    async (findingId: string): Promise<void> => {
      const currentState = getState(findingId);
      const newState: ResolutionState = currentState === 'resolved' ? 'open' : 'resolved';

      setIsUpdating(true);
      setUpdatingId(findingId);
      setError(null);

      try {
        // Call API to update state
        const updated = await findingsApi.updateStatus(findingId, {
          resolutionState: newState,
        });

        // Update local state
        setStates((prev) => {
          const next = new Map(prev);
          next.set(findingId, {
            id: findingId,
            resolutionState: updated.resolutionState,
            updatedAt: new Date(),
          });
          return next;
        });
      } catch (err) {
        console.error('Failed to update finding state:', err);
        setError('ステータスの更新に失敗しました');
        throw err;
      } finally {
        setIsUpdating(false);
        setUpdatingId(null);
      }
    },
    [getState]
  );

  // Update state from a fetched finding detail
  const updateFromDetail = useCallback((finding: FindingDetail): void => {
    setStates((prev) => {
      const next = new Map(prev);
      next.set(finding.id, {
        id: finding.id,
        resolutionState: finding.resolutionState,
        updatedAt: new Date(),
      });
      return next;
    });
  }, []);

  // Update multiple states from summary list
  const updateFromSummaries = useCallback((findings: FindingSummary[]): void => {
    setStates((prev) => {
      const next = new Map(prev);
      findings.forEach((f) => {
        // Only update if we have resolution state info
        // (FindingSummary may not include it)
        if ('resolutionState' in f) {
          next.set(f.id, {
            id: f.id,
            resolutionState: (f as unknown as FindingDetail).resolutionState,
            updatedAt: new Date(),
          });
        }
      });
      return next;
    });
  }, []);

  return {
    states: statesMap,
    isResolved,
    getState,
    toggleResolution,
    updateFromDetail,
    updateFromSummaries,
    isUpdating,
    updatingId,
    error,
  };
}

/**
 * Calculate finding statistics from a list and state map.
 */
export function calculateFindingStats(
  findings: FindingSummary[],
  states: Map<string, ResolutionState>
): {
  total: number;
  open: number;
  resolved: number;
  bySeverity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
} {
  const stats = {
    total: findings.length,
    open: 0,
    resolved: 0,
    bySeverity: {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
    },
  };

  findings.forEach((f) => {
    const state = states.get(f.id) || 'open';
    if (state === 'resolved') {
      stats.resolved++;
    } else {
      stats.open++;
    }

    // Count by severity
    const severity = f.severity as keyof typeof stats.bySeverity;
    if (severity in stats.bySeverity) {
      stats.bySeverity[severity]++;
    }
  });

  return stats;
}
