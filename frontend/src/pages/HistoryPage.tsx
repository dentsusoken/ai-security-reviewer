import { History as HistoryIcon, Loader2, Plus, SearchX } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { HistoryCard, type HistoryItem } from '../features/history/HistoryCard';
import { HistoryFilters, type HistoryFilterState } from '../features/history/HistoryFilters';
import { RereviewModal } from '../features/reviews/RereviewModal';
import { historyApi } from '../services/api';
import type { HistoryReview } from '../types/api';

const INITIAL_FILTERS: HistoryFilterState = {
  search: '',
  period: 'all',
  score: 'all',
  aspect: 'all',
};

// Helper to determine dateKey based on startedAt
const getDateKey = (startedAt: string): HistoryItem['dateKey'] => {
  const date = new Date(startedAt);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'today';
  if (diffDays <= 7) return '7days';
  if (diffDays <= 30) return '30days';
  if (diffDays <= 90) return '90days';
  return 'older';
};

// Helper to format duration
const formatDuration = (ms: number): string => {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${minutes}分${seconds}秒`;
};

// Transform API response to UI format
const transformToHistoryItem = (review: HistoryReview): HistoryItem => {
  return {
    id: review.id,
    repo: review.repoUrl?.split('/').pop() || 'Unknown',
    branch: review.branch || 'main',
    timestamp: new Date(review.startedAt).toLocaleString('ja-JP'),
    duration: formatDuration(review.durationMs || 0),
    score: review.scoreSummary?.overall || 0,
    counts: [
      `●${review.scoreSummary?.critical || 0}`,
      `●${review.scoreSummary?.high || 0}`,
      `●${review.scoreSummary?.medium || 0}`,
      `●${review.scoreSummary?.low || 0}`,
    ],
    dateKey: getDateKey(review.startedAt),
    aspects: review.perspectives || [],
  };
};

export function HistoryPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<HistoryFilterState>(INITIAL_FILTERS);
  const [modalTarget, setModalTarget] = useState<HistoryItem | null>(null);
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Build filter params for API
        const apiFilters: { period?: string; minScore?: number; maxScore?: number; perspective?: string } = {};

        if (filters.period !== 'all') {
          apiFilters.period = filters.period;
        }

        if (filters.score !== 'all') {
          if (filters.score === 'excellent') {
            apiFilters.minScore = 80;
          } else if (filters.score === 'good') {
            apiFilters.minScore = 60;
            apiFilters.maxScore = 79;
          } else if (filters.score === 'warning') {
            apiFilters.minScore = 40;
            apiFilters.maxScore = 59;
          } else if (filters.score === 'danger') {
            apiFilters.maxScore = 39;
          }
        }

        if (filters.aspect !== 'all') {
          apiFilters.perspective = filters.aspect;
        }

        const data = await historyApi.getHistory(apiFilters);
        const items = data.reviews.map(transformToHistoryItem);
        setHistoryItems(items);
      } catch (err) {
        console.error('Failed to fetch history:', err);
        setError('履歴の取得に失敗しました。');
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, [filters.period, filters.score, filters.aspect]);

  // Client-side search filtering
  const filtered = historyItems.filter((item) => {
    if (filters.search && !item.repo.toLowerCase().includes(filters.search.toLowerCase())) {
      return false;
    }
    return true;
  });

  const isFiltered = JSON.stringify(filters) !== JSON.stringify(INITIAL_FILTERS);

  if (isLoading) {
    return (
      <div className="screen-content p-8 flex items-center justify-center">
        <div className="flex items-center gap-3">
          <Loader2 className="w-6 h-6 animate-spin" style={{ color: 'var(--accent-blue)' }} />
          <span>読み込み中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="screen-content p-8 max-w-5xl">
      <div className="flex justify-between items-center mb-8 gap-3 flex-wrap">
        <div>
          <div className="flex items-center gap-2 text-xs mb-2" style={{ color: 'var(--text-tertiary)' }}>
            <HistoryIcon className="w-3 h-3" /><span className="uppercase tracking-wider">HISTORY</span>
          </div>
          <h1 className="text-3xl font-bold">レビュー履歴</h1>
        </div>
        <button onClick={() => navigate('/reviews/new')} className="btn-gradient px-5 py-2.5 rounded-xl font-semibold inline-flex items-center gap-2 text-sm">
          <Plus className="w-4 h-4" />新規レビュー
        </button>
      </div>

      <HistoryFilters value={filters} onChange={setFilters} onClear={() => setFilters(INITIAL_FILTERS)} isFiltered={isFiltered} />

      {error && (
        <div className="mb-4 p-4 rounded-xl text-red-500 text-sm" style={{ background: 'rgba(225,29,72,0.1)' }}>
          {error}
        </div>
      )}

      <div className="mb-4 text-xs" style={{ color: 'var(--text-tertiary)' }}>
        <span>{filtered.length}件</span>のレビュー
      </div>

      {filtered.length > 0 ? (
        <div className="space-y-3">
          {filtered.map((item) => (
            <HistoryCard key={item.id} item={item} onOpen={(id) => navigate(`/reviews/${id}`)} onRereview={(target) => setModalTarget(target)} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <SearchX className="w-12 h-12 mx-auto mb-3" style={{ color: 'var(--text-tertiary)' }} />
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>該当するレビューが見つかりません</p>
          <button onClick={() => setFilters(INITIAL_FILTERS)} className="mt-3 text-xs" style={{ color: 'var(--accent-blue)' }}>
            フィルタをクリア
          </button>
        </div>
      )}

      <RereviewModal
        open={Boolean(modalTarget)}
        onClose={() => setModalTarget(null)}
        target={modalTarget}
        onExecute={() => {
          setModalTarget(null);
          if (modalTarget) {
            navigate(`/reviews/${modalTarget.id}/progress`);
          }
        }}
      />
    </div>
  );
}
