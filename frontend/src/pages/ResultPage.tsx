import { ArrowLeft, CheckCircle, Clock, Download, ExternalLink, FolderGit2, Layers, Loader2, RefreshCw } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { FindingsList } from '../features/findings/FindingsList';
import type { FindingItem } from '../features/findings/FindingCard';
import { ProgressBar } from '../components/ui/ProgressBar';
import { ExportModal } from '../features/reviews/ExportModal';
import { RereviewModal } from '../features/reviews/RereviewModal';
import type { HistoryItem } from '../features/history/HistoryCard';
import { reviewsApi } from '../services/api';
import type { ReviewDetail, FindingSummary } from '../types/api';

export function ResultPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const reviewId = id || 'rs_demo_001';

  const [review, setReview] = useState<ReviewDetail | null>(null);
  const [findings, setFindings] = useState<FindingItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showExport, setShowExport] = useState(false);
  const [showRereview, setShowRereview] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const [reviewData, findingsResponse] = await Promise.all([
          reviewsApi.getById(reviewId),
          reviewsApi.getFindings(reviewId),
        ]);

        setReview(reviewData);

        // Transform API findings to UI format
        const transformedFindings: FindingItem[] = findingsResponse.findings.map((f: FindingSummary) => ({
          id: f.id,
          severity: f.severity.toUpperCase() as FindingItem['severity'],
          title: f.title,
          file: f.filePath + (f.lineStart ? `:${f.lineStart}` : ''),
          standard: [...f.asvsRequirementIds, ...f.cweIds].join(' · '),
        }));
        setFindings(transformedFindings);
      } catch (err) {
        console.error('Failed to fetch review data:', err);
        setError('レビューデータの取得に失敗しました。');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [reviewId]);

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

  if (error || !review) {
    return (
      <div className="screen-content p-8">
        <div className="glass rounded-2xl p-8 text-center">
          <p className="text-red-500 mb-4">{error || 'レビューが見つかりませんでした。'}</p>
          <button
            onClick={() => navigate('/history')}
            className="px-4 py-2 rounded-xl border transition hover:opacity-80"
            style={{ borderColor: 'var(--border)' }}
          >
            履歴に戻る
          </button>
        </div>
      </div>
    );
  }

  // Calculate severity counts from findings
  const severityCounts = {
    CRITICAL: findings.filter(f => f.severity === 'CRITICAL').length,
    HIGH: findings.filter(f => f.severity === 'HIGH').length,
    MEDIUM: findings.filter(f => f.severity === 'MEDIUM').length,
    LOW: findings.filter(f => f.severity === 'LOW').length,
  };

  // Get score and label
  const score = review.scoreSummary?.overall || 0;
  const getScoreColor = (s: number) => s >= 80 ? '#16A34A' : s >= 60 ? '#EA580C' : '#E11D48';
  const getScoreLabel = (s: number) => s >= 80 ? '良好' : s >= 60 ? '要改善' : '要対応';

  // Format duration
  const formatDuration = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}分${seconds}秒`;
  };

  // Build dimensions from perspectiveScores
  const dimensions = review.perspectiveScores?.slice(0, 5).map(d => ({
    name: d.category,
    score: d.percentage,
  })) || [];

  const rereviewTarget: HistoryItem = {
    id: reviewId,
    repo: review.repoUrl?.split('/').pop() || 'Unknown',
    branch: review.branch || 'main',
    timestamp: review.startedAt ? new Date(review.startedAt).toLocaleString('ja-JP') : '',
    duration: formatDuration(review.durationMs || 0),
    score: score,
    counts: [
      `●${severityCounts.CRITICAL}`,
      `●${severityCounts.HIGH}`,
      `●${severityCounts.MEDIUM}`,
      `●${severityCounts.LOW}`,
    ],
    dateKey: 'today',
    aspects: review.perspectives || [],
  };

  return (
    <div className="screen-content p-8 max-w-5xl">
      <div className="flex justify-between items-start mb-8 gap-4 flex-wrap">
        <div>
          <div className="flex items-center gap-2 text-xs mb-2" style={{ color: '#16A34A' }}>
            <CheckCircle className="w-3 h-3" />
            <span className="uppercase tracking-wider font-semibold">Review Complete</span>
          </div>
          <h1 className="text-3xl font-bold mb-3">レビューレポート</h1>
          <div className="flex items-center gap-4 text-sm flex-wrap" style={{ color: 'var(--text-secondary)' }}>
            <span className="flex items-center gap-1.5">
              <FolderGit2 className="w-4 h-4" />
              {review.repoUrl?.split('/').pop() || 'Unknown'}
              {review.branch && (
                <span className="font-mono text-xs px-1.5 py-0.5 rounded" style={{ background: 'var(--bg-elevated)' }}>{review.branch}</span>
              )}
            </span>
            <span className="flex items-center gap-1.5"><Clock className="w-4 h-4" />{formatDuration(review.durationMs || 0)}</span>
            <span className="flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(79,139,255,0.15)', color: 'var(--accent-blue)' }}>
              <FolderGit2 className="w-3 h-3" />{review.inputType === 'github' ? 'GitHub' : review.inputType === 'code' ? 'Code' : 'URL'}
            </span>
            {review.repoUrl && (
              <a href={review.repoUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 hover:underline" style={{ color: 'var(--accent-blue)' }}>
                <ExternalLink className="w-4 h-4" />リポジトリを開く
              </a>
            )}
          </div>
        </div>

        <button onClick={() => setShowExport(true)} className="btn-gradient px-4 py-2.5 rounded-xl font-semibold text-sm inline-flex items-center gap-2">
          <Download className="w-4 h-4" />エクスポート
        </button>
      </div>

      <div className="glass rounded-2xl p-8 mb-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 rounded-full blur-3xl" style={{ background: `${getScoreColor(score)}20` }} />
        <div className="relative grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div>
            <div className="text-xs uppercase tracking-wider mb-3" style={{ color: 'var(--text-tertiary)' }}>総合スコア</div>
            <div className="flex items-baseline gap-3 mb-2">
              <span className="text-7xl font-extrabold" style={{ color: getScoreColor(score) }}>{score}</span>
              <span className="text-2xl" style={{ color: 'var(--text-tertiary)' }}>/100</span>
            </div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm" style={{ background: `${getScoreColor(score)}33`, color: getScoreColor(score) }}>
              {getScoreLabel(score)}
            </div>
          </div>

          <div className="space-y-2">
            {[
              { label: 'Critical', count: severityCounts.CRITICAL, cls: 'badge-critical' },
              { label: 'High', count: severityCounts.HIGH, cls: 'badge-high' },
              { label: 'Medium', count: severityCounts.MEDIUM, cls: 'badge-medium' },
              { label: 'Low', count: severityCounts.LOW, cls: 'badge-low' },
            ].map((item) => (
              <div key={item.label} className={`flex items-center justify-between p-3 rounded-xl ${item.cls}`}>
                <div className="text-sm font-semibold">{item.label}</div>
                <span className="text-xl font-bold">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {dimensions.length > 0 && (
        <>
          <div className="flex items-center gap-2 mb-4">
            <Layers className="w-4 h-4" style={{ color: 'var(--text-tertiary)' }} />
            <h2 className="text-sm font-semibold uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>観点別評価 · OWASP ASVS</h2>
          </div>
          <div className="glass rounded-2xl p-6 mb-8 space-y-4">
            {dimensions.map((item) => {
              const color = item.score >= 80 ? '#16A34A' : item.score >= 60 ? '#EA580C' : '#E11D48';
              const gradient = item.score >= 80 ? 'linear-gradient(90deg, #16A34A, #4ADE80)' : item.score >= 60 ? 'linear-gradient(90deg, #EA580C, #FACC15)' : 'linear-gradient(90deg, #E11D48, #F472B6)';

              return (
                <div key={item.name}>
                  <div className="flex justify-between text-sm mb-2">
                    <span>{item.name}</span>
                    <span className="font-bold font-mono" style={{ color }}>{item.score}%</span>
                  </div>
                  <ProgressBar value={item.score} heightClassName="h-1.5" gradient={gradient} />
                </div>
              );
            })}
            {review.perspectiveScores && review.perspectiveScores.length > 5 && (
              <div className="text-xs pt-1 text-center" style={{ color: 'var(--text-tertiary)' }}>▼ 残り{review.perspectiveScores.length - 5}項目を展開</div>
            )}
          </div>
        </>
      )}

      <FindingsList findings={findings} onSelect={(findingId) => navigate(`/reviews/${reviewId}/findings/${findingId}`)} />

      <div className="flex justify-between mt-8 pt-6 border-t" style={{ borderColor: 'var(--border)' }}>
        <button onClick={() => navigate('/history')} className="px-5 py-2.5 rounded-xl border transition hover:opacity-80 text-sm inline-flex items-center gap-2" style={{ borderColor: 'var(--border)' }}>
          <ArrowLeft className="w-4 h-4" />履歴に戻る
        </button>
        <button onClick={() => setShowRereview(true)} className="btn-gradient px-5 py-2.5 rounded-xl font-semibold text-sm inline-flex items-center gap-2">
          <RefreshCw className="w-4 h-4" />再レビュー
        </button>
      </div>

      <ExportModal open={showExport} onClose={() => setShowExport(false)} reviewId={reviewId} />
      <RereviewModal
        open={showRereview}
        onClose={() => setShowRereview(false)}
        target={rereviewTarget}
        onExecute={() => navigate(`/reviews/${reviewId}/progress`)}
      />
    </div>
  );
}
