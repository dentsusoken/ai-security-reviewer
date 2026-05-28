/**
 * Persistent AI Agent Status Badge component.
 *
 * Shows a small badge in the header/layout indicating when AI agents
 * are actively processing reviews. Clicking navigates to the progress page.
 */
import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, Loader2, Check, AlertTriangle } from 'lucide-react';

export type AIAgentStatusType = 'idle' | 'processing' | 'completed' | 'error';

interface AIAgentStatusBadgeProps {
  /** Current status of the AI agent */
  status?: AIAgentStatusType;
  /** Active review session ID (for navigation) */
  activeReviewId?: string | null;
  /** Progress percentage (0-100) when processing */
  progress?: number;
  /** Whether the badge should pulse to attract attention */
  pulse?: boolean;
}

/**
 * A persistent status badge that shows when AI agents are active.
 *
 * Appears in the header/layout and provides quick access to the
 * active review's progress page.
 */
export function AIAgentStatusBadge({
  status = 'idle',
  activeReviewId,
  progress = 0,
  pulse = false,
}: AIAgentStatusBadgeProps) {
  const navigate = useNavigate();
  const [isHovered, setIsHovered] = useState(false);

  // Don't render when idle
  if (status === 'idle') {
    return null;
  }

  const handleClick = useCallback(() => {
    if (activeReviewId) {
      navigate(`/reviews/${activeReviewId}/progress`);
    }
  }, [activeReviewId, navigate]);

  // Status-specific styling
  const getStatusStyles = () => {
    switch (status) {
      case 'processing':
        return {
          bg: 'rgba(79, 139, 255, 0.2)',
          border: 'rgba(79, 139, 255, 0.5)',
          text: 'var(--accent-blue)',
          label: 'AI処理中',
        };
      case 'completed':
        return {
          bg: 'rgba(34, 197, 94, 0.2)',
          border: 'rgba(34, 197, 94, 0.5)',
          text: '#22C55E',
          label: '完了',
        };
      case 'error':
        return {
          bg: 'rgba(239, 68, 68, 0.2)',
          border: 'rgba(239, 68, 68, 0.5)',
          text: '#EF4444',
          label: 'エラー',
        };
      default:
        return {
          bg: 'rgba(100, 116, 139, 0.2)',
          border: 'rgba(100, 116, 139, 0.5)',
          text: 'var(--text-secondary)',
          label: '',
        };
    }
  };

  const styles = getStatusStyles();

  const renderIcon = () => {
    switch (status) {
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin" style={{ color: styles.text }} />;
      case 'completed':
        return <Check className="w-4 h-4" style={{ color: styles.text }} />;
      case 'error':
        return <AlertTriangle className="w-4 h-4" style={{ color: styles.text }} />;
      default:
        return <Bot className="w-4 h-4" style={{ color: styles.text }} />;
    }
  };

  return (
    <button
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        inline-flex items-center gap-2 px-3 py-1.5 rounded-full
        border transition-all duration-200
        ${pulse && status === 'processing' ? 'animate-pulse' : ''}
        ${isHovered ? 'scale-105' : ''}
      `}
      style={{
        background: styles.bg,
        borderColor: styles.border,
        cursor: activeReviewId ? 'pointer' : 'default',
      }}
      disabled={!activeReviewId}
      title={activeReviewId ? 'クリックして進捗を確認' : undefined}
    >
      {renderIcon()}
      <span className="text-xs font-medium" style={{ color: styles.text }}>
        {styles.label}
      </span>
      {status === 'processing' && progress > 0 && (
        <span className="text-xs" style={{ color: styles.text }}>
          {progress}%
        </span>
      )}
    </button>
  );
}

/**
 * Hook to manage AI agent status across the app.
 *
 * Tracks active reviews and provides status updates.
 */
export function useAIAgentStatus() {
  const [status, setStatus] = useState<AIAgentStatusType>('idle');
  const [activeReviewId, setActiveReviewId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  // Check for active reviews in local storage or state
  useEffect(() => {
    const stored = localStorage.getItem('activeReviewId');
    if (stored) {
      setActiveReviewId(stored);
      setStatus('processing');
    }
  }, []);

  // Set active review
  const startReview = useCallback((reviewId: string) => {
    setActiveReviewId(reviewId);
    setStatus('processing');
    setProgress(0);
    localStorage.setItem('activeReviewId', reviewId);
  }, []);

  // Update progress
  const updateProgress = useCallback((percent: number) => {
    setProgress(percent);
  }, []);

  // Complete review
  const completeReview = useCallback(() => {
    setStatus('completed');
    setProgress(100);
    localStorage.removeItem('activeReviewId');
    // Clear after a delay
    setTimeout(() => {
      setStatus('idle');
      setActiveReviewId(null);
      setProgress(0);
    }, 5000);
  }, []);

  // Error in review
  const setError = useCallback(() => {
    setStatus('error');
    localStorage.removeItem('activeReviewId');
    // Clear after a delay
    setTimeout(() => {
      setStatus('idle');
      setActiveReviewId(null);
      setProgress(0);
    }, 10000);
  }, []);

  // Clear status
  const clearStatus = useCallback(() => {
    setStatus('idle');
    setActiveReviewId(null);
    setProgress(0);
    localStorage.removeItem('activeReviewId');
  }, []);

  return {
    status,
    activeReviewId,
    progress,
    startReview,
    updateProgress,
    completeReview,
    setError,
    clearStatus,
  };
}
