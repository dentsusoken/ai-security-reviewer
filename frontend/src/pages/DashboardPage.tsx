import { useNavigate } from 'react-router-dom';
import { Sparkles, Zap, BarChart3, FileCheck, AlertTriangle, CheckCircle2, TrendingUp, FolderGit2, Clock, ChevronRight, ArrowRight, Loader2 } from 'lucide-react';
import { GlassCard } from '../components/ui/GlassCard';
import { useDashboard, formatTimestamp, getRepoName } from '../features/dashboard';
import { useAuth } from '../features/auth';

export function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { stats, recentReviews, loading, error } = useDashboard();

  // Get user display name
  const getUserName = () => {
    if (user?.name) return user.name;
    if (user?.email) return user.email.split('@')[0];
    return 'テストユーザー';
  };

  if (loading) {
    return (
      <div className="p-8 max-w-6xl flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin" style={{ color: 'var(--accent-blue)' }} />
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="p-8 max-w-6xl">
        <div className="glass rounded-2xl p-8 text-center">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4" style={{ color: '#EA580C' }} />
          <p className="text-lg font-semibold mb-2">読み込みエラー</p>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 rounded-lg border hover:opacity-80"
            style={{ borderColor: 'var(--border)' }}
          >
            再試行
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl">
      {/* Welcome Section */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-xs mb-2" style={{ color: 'var(--text-tertiary)' }}>
          <Sparkles className="w-3 h-3" />
          <span>Welcome back</span>
        </div>
        <h1 className="text-3xl font-bold">
          こんにちは、<span className="gradient-text">{getUserName()}</span>さん
        </h1>
      </div>

      {/* Quick Start Card */}
      <GlassCard className="relative rounded-2xl p-8 overflow-hidden mb-8">
        <div className="absolute top-0 right-0 w-80 h-80 rounded-full blur-3xl" style={{ background: 'rgba(79,139,255,0.15)' }}></div>
        <div className="relative">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs mb-4" style={{ background: 'var(--bg-elevated)' }}>
            <Zap className="w-3 h-3" style={{ color: '#EAB308' }} />
            <span>Quick Start</span>
          </div>
          <h2 className="text-2xl font-bold mb-2">新しいレビューを開始</h2>
          <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>
            GitHubリポジトリを指定してAIエージェントによる
            <br />
            セキュリティレビューを実行します
          </p>
          <button
            onClick={() => navigate('/reviews/new')}
            className="btn-gradient px-6 py-3 rounded-xl font-semibold inline-flex items-center gap-2 hover:scale-105 transition-transform"
          >
            <span>+</span>
            新規レビュー開始
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </GlassCard>

      {/* Stats Section */}
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-4 h-4" style={{ color: 'var(--text-tertiary)' }} />
        <h2 className="text-sm font-semibold uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
          統計
        </h2>
      </div>
      <div className="grid grid-cols-4 gap-4 mb-10">
        {/* Total Reviews */}
        <GlassCard className="rounded-2xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: 'rgba(79,139,255,0.2)' }}>
              <FileCheck className="w-4 h-4" style={{ color: 'var(--accent-blue)' }} />
            </div>
            <span className="text-xs font-semibold" style={{ color: '#16A34A' }}>
              +3
            </span>
          </div>
          <div className="text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>
            総レビュー
          </div>
          <div className="text-3xl font-bold">{stats.totalReviews}</div>
        </GlassCard>

        {/* Total Findings */}
        <GlassCard className="rounded-2xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: 'rgba(234,88,12,0.2)' }}>
              <AlertTriangle className="w-4 h-4" style={{ color: '#EA580C' }} />
            </div>
          </div>
          <div className="text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>
            検出済
          </div>
          <div className="text-3xl font-bold" style={{ color: '#EA580C' }}>
            {stats.totalFindings}
          </div>
        </GlassCard>

        {/* Fixed */}
        <GlassCard className="rounded-2xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: 'rgba(22,163,74,0.2)' }}>
              <CheckCircle2 className="w-4 h-4" style={{ color: '#16A34A' }} />
            </div>
            <span className="text-xs font-semibold" style={{ color: '#16A34A' }}>
              {stats.totalFindings > 0 ? Math.round((stats.resolvedFindings / stats.totalFindings) * 100) : 0}%
            </span>
          </div>
          <div className="text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>
            修正済
          </div>
          <div className="text-3xl font-bold" style={{ color: '#16A34A' }}>
            {stats.resolvedFindings}
          </div>
        </GlassCard>

        {/* Average Score */}
        <GlassCard className="rounded-2xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: 'rgba(167,139,250,0.2)' }}>
              <TrendingUp className="w-4 h-4" style={{ color: 'var(--accent-purple)' }} />
            </div>
            <span className="text-xs font-semibold" style={{ color: '#16A34A' }}>
              ↑5
            </span>
          </div>
          <div className="text-xs mb-1" style={{ color: 'var(--text-tertiary)' }}>
            平均スコア
          </div>
          <div className="text-3xl font-bold">
            <span className="gradient-text">{stats.averageScore}</span>
            <span className="text-base" style={{ color: 'var(--text-tertiary)' }}>
              /100
            </span>
          </div>
        </GlassCard>
      </div>

      {/* Recent Reviews */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4" style={{ color: 'var(--text-tertiary)' }} />
          <h2 className="text-sm font-semibold uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
            最近のレビュー
          </h2>
        </div>
        <button
          onClick={() => navigate('/history')}
          className="text-sm inline-flex items-center gap-1 hover:underline"
          style={{ color: 'var(--accent-blue)' }}
        >
          すべて見る <ArrowRight className="w-3 h-3" />
        </button>
      </div>

      <GlassCard className="rounded-2xl overflow-hidden">
        {recentReviews.map((review, idx) => (
          <div
            key={review.id}
            onClick={() => navigate(`/reviews/${review.id}`)}
            className={`p-5 cursor-pointer transition hover-row flex items-center justify-between ${
              idx < recentReviews.length - 1 ? 'border-b' : ''
            }`}
            style={{ borderColor: 'var(--border)' }}
          >
            <div className="flex items-center gap-4">
              <div
                className="w-11 h-11 rounded-xl flex items-center justify-center"
                style={{
                  background:
                    review.scoreSummary.overall < 70
                      ? 'linear-gradient(135deg, rgba(234,88,12,0.2), rgba(225,29,72,0.2))'
                      : 'linear-gradient(135deg, rgba(22,163,74,0.2), rgba(8,145,178,0.2))',
                }}
              >
                <FolderGit2
                  className="w-5 h-5"
                  style={{
                    color: review.scoreSummary.overall < 70 ? '#EA580C' : '#16A34A',
                  }}
                />
              </div>
              <div>
                <div className="font-semibold flex items-center gap-2">
                  {getRepoName(review.repoUrl)}
                  <span
                    className="text-xs px-2 py-0.5 rounded font-mono"
                    style={{ background: 'var(--bg-elevated)', color: 'var(--text-tertiary)' }}
                  >
                    {review.branch}
                  </span>
                </div>
                <div className="text-xs mt-1 flex items-center gap-3" style={{ color: 'var(--text-tertiary)' }}>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {formatTimestamp(review.startedAt)}
                  </span>
                  <span style={{ color: '#E11D48' }}>●{review.scoreSummary.critical}</span>
                  <span style={{ color: '#EA580C' }}>●{review.scoreSummary.high}</span>
                  <span style={{ color: '#CA8A04' }}>●{review.scoreSummary.medium}</span>
                  <span style={{ color: '#16A34A' }}>●{review.scoreSummary.low}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-2xl font-bold" style={{ color: review.scoreSummary.overall < 70 ? '#EA580C' : '#16A34A' }}>
                  {review.scoreSummary.overall}
                </div>
                <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
                  /100
                </div>
              </div>
              <ChevronRight className="w-5 h-5" style={{ color: 'var(--text-tertiary)' }} />
            </div>
          </div>
        ))}
      </GlassCard>
    </div>
  );
}
