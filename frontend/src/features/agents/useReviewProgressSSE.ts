/**
 * Custom hook for SSE-based review progress streaming.
 *
 * Encapsulates SSE connection, event handling, reconnection logic,
 * and state management for real-time review progress.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { connectReviewEvents } from '../../services/api';
import type {
  BackendProgressEvent,
  BackendAgentProgressEvent,
  BackendFetchingEvent,
  BackendCompletedEvent,
  BackendErrorEvent,
} from '../../services/api/events';

/**
 * Agent state for display.
 */
export interface AgentState {
  /** Display title (e.g., "🧠 SpecComplianceAgent") */
  title: string;
  /** Current activity description */
  description: string;
  /** Execution status */
  status: 'waiting' | 'running' | 'completed' | 'failed';
  /** Progress percentage (0-100) */
  progress?: number;
  /** Status chips (e.g., severity counts) */
  chips?: string[];
  /** Additional details */
  details?: string;
}

/**
 * Review progress state returned by the hook.
 */
export interface ReviewProgressState {
  /** Overall progress percentage (0-100) */
  overallProgress: number;
  /** Elapsed time in milliseconds */
  elapsedMs: number;
  /** Estimated remaining time in milliseconds */
  estimatedRemainingMs: number;
  /** Agent states keyed by agent name */
  agents: Record<string, AgentState>;
  /** Log lines for display */
  logLines: string[];
  /** Whether review is completed */
  isCompleted: boolean;
  /** Whether review has an error */
  hasError: boolean;
  /** Error message if any */
  errorMessage: string | null;
  /** Whether SSE is connected */
  isConnected: boolean;
  /** Reconnection attempt count */
  reconnectAttempts: number;
}

/**
 * Default agent state for initial render.
 */
const DEFAULT_AGENTS: Record<string, AgentState> = {
  repo: {
    title: '📥 リポジトリ取得',
    description: '準備中...',
    status: 'waiting',
  },
  SpecComplianceAgent: {
    title: '🧠 SpecComplianceAgent',
    description: 'OWASP ASVS 14カテゴリを評価',
    status: 'waiting',
  },
};

/**
 * Maximum log lines to keep.
 */
const MAX_LOG_LINES = 100;

/**
 * Maximum reconnection attempts.
 */
const MAX_RECONNECT_ATTEMPTS = 5;

/**
 * Reconnection delay in milliseconds.
 */
const RECONNECT_DELAY_MS = 2000;

/**
 * Custom hook for SSE-based review progress streaming.
 *
 * @param reviewId - The review session ID to subscribe to
 * @param options - Optional configuration
 * @returns Review progress state
 */
export function useReviewProgressSSE(
  reviewId: string,
  options?: {
    /** Auto-connect on mount (default: true) */
    autoConnect?: boolean;
    /** Callback when review completes */
    onCompleted?: (data: BackendCompletedEvent) => void;
    /** Callback when error occurs */
    onError?: (error: BackendErrorEvent) => void;
  }
): ReviewProgressState & {
  /** Connect to SSE stream */
  connect: () => void;
  /** Disconnect from SSE stream */
  disconnect: () => void;
  /** Format elapsed time as string */
  formatElapsedTime: () => string;
  /** Get estimated remaining time as string */
  getEstimatedRemaining: () => string;
} {
  const { autoConnect = true, onCompleted, onError } = options || {};

  // State
  const [overallProgress, setOverallProgress] = useState(0);
  const [agents, setAgents] = useState<Record<string, AgentState>>(DEFAULT_AGENTS);
  const [logLines, setLogLines] = useState<string[]>([]);
  const [isCompleted, setIsCompleted] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  // Timing state
  const [startTime] = useState(() => Date.now());
  const [elapsedMs, setElapsedMs] = useState(0);
  const [estimatedRemainingMs, setEstimatedRemainingMs] = useState(0);

  // Refs for cleanup
  const cleanupRef = useRef<(() => void) | null>(null);
  const timerRef = useRef<number | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // Add log line with timestamp
  const addLog = useCallback((message: string) => {
    const timestamp = new Date().toLocaleTimeString('ja-JP');
    setLogLines(prev => [...prev.slice(-(MAX_LOG_LINES - 1)), `[${timestamp}] ${message}`]);
  }, []);

  // Handle progress events
  const handleProgress = useCallback((data: BackendProgressEvent) => {
    setOverallProgress(data.percent);
    if (data.message) {
      addLog(data.message);
    }
  }, [addLog]);

  // Handle agent progress events
  const handleAgentProgress = useCallback((data: BackendAgentProgressEvent) => {
    const agentKey = data.agent_name;

    setAgents(prev => ({
      ...prev,
      [agentKey]: {
        ...prev[agentKey],
        title: prev[agentKey]?.title || `🤖 ${agentKey}`,
        status: data.status as AgentState['status'],
        progress: data.progress_percent,
        description: data.message || prev[agentKey]?.description || '',
      },
    }));

    if (data.message) {
      addLog(`[${data.agent_name}] ${data.message}`);
    }
  }, [addLog]);

  // Handle fetching events
  const handleFetching = useCallback((eventType: string, data: BackendFetchingEvent) => {
    if (eventType === 'fetching_repo' || eventType === 'fetching_tree') {
      setAgents(prev => ({
        ...prev,
        repo: {
          ...prev.repo,
          status: 'running',
          description: data.message,
        },
      }));
    } else if (eventType === 'files_found' || eventType === 'files_fetched') {
      const isComplete = eventType === 'files_fetched';
      setAgents(prev => ({
        ...prev,
        repo: {
          ...prev.repo,
          status: isComplete ? 'completed' : 'running',
          description: data.message,
          details: data.file_count ? `${data.file_count} files` : undefined,
        },
      }));
    } else if (eventType === 'fetching_file') {
      setAgents(prev => ({
        ...prev,
        repo: {
          ...prev.repo,
          status: 'running',
          description: data.message,
          progress: data.current && data.total
            ? Math.round((data.current / data.total) * 100)
            : undefined,
        },
      }));
    } else if (eventType === 'analyzing_code') {
      setAgents(prev => ({
        ...prev,
        repo: {
          ...prev.repo,
          status: 'completed',
        },
        SpecComplianceAgent: {
          ...prev.SpecComplianceAgent,
          status: 'running',
          description: data.message,
        },
      }));
    }

    if (data.message) {
      addLog(data.message);
    }
  }, [addLog]);

  // Handle completion
  const handleCompleted = useCallback((data: BackendCompletedEvent) => {
    setIsCompleted(true);
    setOverallProgress(100);
    setIsConnected(false);

    // Mark all agents as completed
    setAgents(prev => {
      const updated = { ...prev };
      Object.keys(updated).forEach(key => {
        if (updated[key].status === 'running' || updated[key].status === 'waiting') {
          updated[key] = { ...updated[key], status: 'completed' };
        }
      });
      return updated;
    });

    addLog(`✅ レビュー完了: スコア ${data.overall_score}, ${data.findings_count} 件の指摘`);
    onCompleted?.(data);

    // Stop timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  }, [addLog, onCompleted]);

  // Handle errors
  const handleError = useCallback((error: BackendErrorEvent) => {
    setHasError(true);
    setErrorMessage(error.message);
    setIsConnected(false);

    // Mark running agents as failed
    setAgents(prev => {
      const updated = { ...prev };
      Object.keys(updated).forEach(key => {
        if (updated[key].status === 'running') {
          updated[key] = { ...updated[key], status: 'failed' };
        }
      });
      return updated;
    });

    addLog(`❌ エラー: ${error.message}`);
    onError?.(error);

    // Stop timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    // Try to reconnect
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectTimeoutRef.current = window.setTimeout(() => {
        setReconnectAttempts(prev => prev + 1);
        addLog(`再接続を試行中... (${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`);
        connect();
      }, RECONNECT_DELAY_MS);
    }
  }, [addLog, onError, reconnectAttempts]);

  // Connect to SSE
  const connect = useCallback(() => {
    // Disconnect if already connected
    if (cleanupRef.current) {
      cleanupRef.current();
    }

    addLog('SSE接続を開始...');
    setIsConnected(true);

    cleanupRef.current = connectReviewEvents(reviewId, {
      onProgress: handleProgress,
      onAgentProgress: handleAgentProgress,
      onFetching: handleFetching,
      onCompleted: handleCompleted,
      onError: handleError,
      onLog: addLog,
    });
  }, [reviewId, handleProgress, handleAgentProgress, handleFetching, handleCompleted, handleError, addLog]);

  // Disconnect from SSE
  const disconnect = useCallback(() => {
    if (cleanupRef.current) {
      cleanupRef.current();
      cleanupRef.current = null;
    }
    setIsConnected(false);
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [autoConnect, connect, disconnect]);

  // Elapsed time timer
  useEffect(() => {
    timerRef.current = window.setInterval(() => {
      const elapsed = Date.now() - startTime;
      setElapsedMs(elapsed);

      // Calculate estimated remaining time
      if (overallProgress > 0 && overallProgress < 100) {
        const estimatedTotalMs = (elapsed / overallProgress) * 100;
        setEstimatedRemainingMs(Math.max(0, estimatedTotalMs - elapsed));
      }
    }, 1000);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [startTime, overallProgress]);

  // Format time helper
  const formatElapsedTime = useCallback(() => {
    const minutes = Math.floor(elapsedMs / 60000);
    const seconds = Math.floor((elapsedMs % 60000) / 1000);
    return `${minutes}分${seconds}秒`;
  }, [elapsedMs]);

  // Get estimated remaining as string
  const getEstimatedRemaining = useCallback(() => {
    if (overallProgress >= 100 || isCompleted) return '完了';
    if (overallProgress === 0) return '計算中...';
    if (estimatedRemainingMs < 5000) return 'まもなく完了';

    const minutes = Math.floor(estimatedRemainingMs / 60000);
    const seconds = Math.floor((estimatedRemainingMs % 60000) / 1000);
    return `残り約 ${minutes}分${seconds}秒`;
  }, [overallProgress, isCompleted, estimatedRemainingMs]);

  return {
    overallProgress,
    elapsedMs,
    estimatedRemainingMs,
    agents,
    logLines,
    isCompleted,
    hasError,
    errorMessage,
    isConnected,
    reconnectAttempts,
    connect,
    disconnect,
    formatElapsedTime,
    getEstimatedRemaining,
  };
}
