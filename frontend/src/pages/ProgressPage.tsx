import { FastForward } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { AgentStatusCard } from '../features/agents/AgentStatusCard';
import { LiveLog } from '../features/agents/LiveLog';
import { ProgressBar } from '../components/ui/ProgressBar';
import { connectReviewEvents } from '../services/api';
import type {
  BackendProgressEvent,
  BackendAgentProgressEvent,
  BackendFetchingEvent,
  BackendCompletedEvent,
  BackendErrorEvent,
} from '../services/api/events';

interface AgentState {
  title: string;
  description: string;
  status: 'waiting' | 'running' | 'completed' | 'failed';
  progress?: number;
  chips?: string[];
  details?: string;
}

interface LocationState {
  repoUrl?: string;
  branch?: string;
}

export function ProgressPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();
  const reviewId = id || 'demo-001';

  // Extract repo info from location state (passed from NewReviewPage)
  const locationState = location.state as LocationState | undefined;
  const repoUrl = locationState?.repoUrl || '';
  const branch = locationState?.branch || 'main';

  // Parse repo name from URL
  const getRepoDisplayName = () => {
    if (!repoUrl) return 'Repository';
    try {
      const match = repoUrl.match(/github\.com\/([^/]+\/[^/]+)/);
      return match ? match[1] : repoUrl;
    } catch {
      return repoUrl;
    }
  };

  const [overallProgress, setOverallProgress] = useState(0);
  const [startTime] = useState(() => Date.now());
  const [elapsedMs, setElapsedMs] = useState(0);
  const [logLines, setLogLines] = useState<string[]>([]);
  const [isCompleted, setIsCompleted] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [agents, setAgents] = useState<Record<string, AgentState>>({
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
  });

  // Elapsed time timer
  const timerRef = useRef<number | null>(null);
  useEffect(() => {
    timerRef.current = window.setInterval(() => {
      setElapsedMs(Date.now() - startTime);
    }, 1000);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [startTime]);

  // Format elapsed time
  const formatTime = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}分${seconds}秒`;
  };

  // Estimate remaining time based on progress (assume ~60s total for standard review)
  const getEstimatedRemaining = () => {
    if (overallProgress >= 100 || isCompleted) return '完了';
    if (overallProgress === 0) return '計算中...';

    // Estimate based on current progress and elapsed time
    const estimatedTotalMs = (elapsedMs / overallProgress) * 100;
    const remainingMs = Math.max(0, estimatedTotalMs - elapsedMs);

    if (remainingMs < 5000) return 'まもなく完了';
    return `残り約 ${formatTime(remainingMs)}`;
  };

  // Handle progress events
  const handleProgress = useCallback((data: BackendProgressEvent) => {
    setOverallProgress(data.percent);
  }, []);

  // Handle agent progress events
  const handleAgentProgress = useCallback((data: BackendAgentProgressEvent) => {
    const agentKey = data.agent_name;

    setAgents((prev) => ({
      ...prev,
      [agentKey]: {
        ...prev[agentKey],
        title: prev[agentKey]?.title || `🤖 ${agentKey}`,
        status: data.status as AgentState['status'],
        progress: data.progress_percent,
        description: data.message || prev[agentKey]?.description || '',
      },
    }));
  }, []);

  // Handle fetching events (repo, files, etc.)
  const handleFetching = useCallback((eventType: string, data: BackendFetchingEvent) => {
    if (eventType === 'fetching_repo' || eventType === 'fetching_tree') {
      setAgents((prev) => ({
        ...prev,
        repo: {
          ...prev.repo,
          status: 'running',
          description: data.message,
        },
      }));
    } else if (eventType === 'files_found' || eventType === 'files_fetched') {
      const isComplete = eventType === 'files_fetched';
      setAgents((prev) => ({
        ...prev,
        repo: {
          ...prev.repo,
          status: isComplete ? 'completed' : 'running',
          description: data.message,
          details: data.file_count ? `${data.file_count} files` : undefined,
        },
      }));
    } else if (eventType === 'fetching_file') {
      setAgents((prev) => ({
        ...prev,
        repo: {
          ...prev.repo,
          status: 'running',
          description: data.message,
          progress:
            data.current && data.total ? Math.round((data.current / data.total) * 100) : undefined,
        },
      }));
    } else if (eventType === 'analyzing_code') {
      // Mark repo as completed and start AI agent
      setAgents((prev) => ({
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
  }, []);

  // Handle log events
  const handleLog = useCallback((message: string) => {
    const timestamp = new Date().toLocaleTimeString('ja-JP');
    setLogLines((prev) => [...prev.slice(-49), `[${timestamp}] ${message}`]);
  }, []);

  // Handle completion
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleCompleted = useCallback(
    (_data?: BackendCompletedEvent) => {
      setIsCompleted(true);
      setOverallProgress(100);

      // Mark all agents as completed
      setAgents((prev) => {
        const updated = { ...prev };
        Object.keys(updated).forEach((key) => {
          if (updated[key].status === 'running' || updated[key].status === 'waiting') {
            updated[key] = { ...updated[key], status: 'completed' };
          }
        });
        return updated;
      });

      // Stop the timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }

      // Auto-navigate after a short delay
      setTimeout(() => {
        navigate(`/reviews/${reviewId}`);
      }, 2000);
    },
    [navigate, reviewId]
  );

  // Handle errors
  const handleError = useCallback((error: BackendErrorEvent) => {
    setHasError(true);
    setErrorMessage(error.message);

    // Mark running agents as failed
    setAgents((prev) => {
      const updated = { ...prev };
      Object.keys(updated).forEach((key) => {
        if (updated[key].status === 'running') {
          updated[key] = { ...updated[key], status: 'failed' };
        }
      });
      return updated;
    });

    // Stop the timer
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  }, []);

  // Connect to SSE
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- Initial log message for SSE connection
    handleLog('SSE接続を開始...');

    const cleanup = connectReviewEvents(reviewId, {
      onProgress: handleProgress,
      onAgentProgress: handleAgentProgress,
      onFetching: handleFetching,
      onCompleted: handleCompleted,
      onError: handleError,
      onLog: handleLog,
    });

    return () => {
      cleanup();
    };
  }, [
    reviewId,
    handleProgress,
    handleAgentProgress,
    handleFetching,
    handleCompleted,
    handleError,
    handleLog,
  ]);

  const getStatusText = () => {
    if (hasError) return 'エラー発生';
    if (isCompleted) return 'Review Complete';
    return 'AI Agents Working';
  };

  const getHeaderText = () => {
    if (hasError) return 'レビューエラー';
    if (isCompleted) return 'レビュー完了';
    return 'レビュー実行中';
  };

  return (
    <div className="screen-content p-8 max-w-4xl">
      <div className="mb-8">
        <div
          className="flex items-center gap-2 text-xs mb-2"
          style={{ color: hasError ? 'var(--accent-red)' : 'var(--accent-blue)' }}
        >
          <span className="relative flex w-2 h-2">
            {!isCompleted && !hasError && (
              <span
                className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                style={{ background: 'var(--accent-blue)' }}
              />
            )}
            <span
              className="relative inline-flex rounded-full h-2 w-2"
              style={{ background: hasError ? 'var(--accent-red)' : 'var(--accent-blue)' }}
            />
          </span>
          <span className="uppercase tracking-wider font-semibold">{getStatusText()}</span>
        </div>
        <h1 className="text-3xl font-bold">{getHeaderText()}</h1>
        <p className="mt-2 font-mono text-sm" style={{ color: 'var(--text-secondary)' }}>
          {getRepoDisplayName()} / {branch}
        </p>
      </div>

      {hasError && errorMessage && (
        <div
          className="glass rounded-2xl p-4 mb-6 border"
          style={{ borderColor: 'var(--accent-red)', background: 'rgba(239, 68, 68, 0.1)' }}
        >
          <p className="text-sm" style={{ color: 'var(--accent-red)' }}>
            ❌ {errorMessage}
          </p>
        </div>
      )}

      <div className="glass rounded-2xl p-6 mb-6">
        <div className="flex justify-between items-center mb-3">
          <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            全体進捗
          </span>
          <span className="text-2xl font-bold gradient-text">{overallProgress}%</span>
        </div>
        <ProgressBar value={overallProgress} showShimmer={!isCompleted && !hasError} />
        <div
          className="flex justify-between mt-3 text-xs font-mono"
          style={{ color: 'var(--text-tertiary)' }}
        >
          <span>経過 {formatTime(elapsedMs)}</span>
          <span>{getEstimatedRemaining()}</span>
        </div>
      </div>

      <div className="space-y-3 mb-6">
        {Object.entries(agents).map(([key, agent]) => (
          <AgentStatusCard
            key={key}
            title={agent.title}
            description={agent.description}
            status={agent.status}
            progress={agent.progress}
            chips={agent.chips}
            details={agent.details}
          />
        ))}
      </div>

      <LiveLog lines={logLines.length > 0 ? logLines : ['接続中...']} />

      <div className="flex justify-center gap-3 mt-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="px-5 py-2.5 rounded-xl border transition hover:opacity-80 text-sm"
          style={{ borderColor: 'var(--border)' }}
        >
          バックグラウンド実行
        </button>
        {hasError ? (
          <button
            onClick={() => navigate('/reviews/new')}
            className="btn-gradient px-5 py-2.5 rounded-xl font-semibold inline-flex items-center gap-2 text-sm"
          >
            やり直す
          </button>
        ) : (
          <button
            onClick={() => navigate(`/reviews/${reviewId}`)}
            className="btn-gradient px-5 py-2.5 rounded-xl font-semibold inline-flex items-center gap-2 text-sm"
          >
            {isCompleted ? (
              <>結果を表示</>
            ) : (
              <>
                <FastForward className="w-4 h-4" />
                結果へ（デモ用スキップ）
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
