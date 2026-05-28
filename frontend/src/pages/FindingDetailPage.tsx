import { AlertOctagon, ArrowLeft, ArrowRight, BookMarked, BookOpen, CheckCircle, Copy, File, Loader2, Search, Sparkles, Undo2, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useToast } from '../features/reviews/ToastProvider';
import { findingsApi } from '../services/api';
import type { FindingDetail, Severity, ResolutionState } from '../types/api';

const severityLabels: Record<Severity, string> = {
  critical: 'CRITICAL',
  high: 'HIGH',
  medium: 'MEDIUM',
  low: 'LOW',
};

const severityClasses: Record<Severity, string> = {
  critical: 'badge-critical',
  high: 'badge-high',
  medium: 'badge-medium',
  low: 'badge-low',
};

const severityColors: Record<Severity, string> = {
  critical: 'rgba(225,29,72,0.1)',
  high: 'rgba(234,88,12,0.1)',
  medium: 'rgba(234,179,8,0.1)',
  low: 'rgba(59,130,246,0.1)',
};

export function FindingDetailPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { findingId } = useParams();

  const [finding, setFinding] = useState<FindingDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    const fetchFinding = async () => {
      if (!findingId) return;

      try {
        setIsLoading(true);
        setError(null);
        const data = await findingsApi.getById(findingId);
        setFinding(data);
      } catch (err) {
        console.error('Failed to fetch finding:', err);
        setError('指摘詳細の取得に失敗しました。');
      } finally {
        setIsLoading(false);
      }
    };

    fetchFinding();
  }, [findingId]);

  const handleToggleResolved = async () => {
    if (!finding || !findingId) return;

    const newStatus: ResolutionState = finding.resolutionState === 'resolved' ? 'open' : 'resolved';

    try {
      setIsUpdating(true);
      const updated = await findingsApi.updateStatus(findingId, { resolutionState: newStatus });
      setFinding(updated);
      showToast(
        newStatus === 'resolved' ? '対応済みにマークしました' : '未対応に戻しました',
        'info'
      );
    } catch (err) {
      console.error('Failed to update finding status:', err);
      showToast('ステータスの更新に失敗しました', 'error');
    } finally {
      setIsUpdating(false);
    }
  };

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

  if (error || !finding) {
    return (
      <div className="screen-content p-8">
        <div className="glass rounded-2xl p-8 text-center">
          <p className="text-red-500 mb-4">{error || '指摘が見つかりませんでした。'}</p>
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 rounded-xl border transition hover:opacity-80"
            style={{ borderColor: 'var(--border)' }}
          >
            戻る
          </button>
        </div>
      </div>
    );
  }

  const resolved = finding.resolutionState === 'resolved';
  const severity = finding.severity;
  const severityClass = severityClasses[severity] || 'badge-low';
  const severityColor = severityColors[severity] || 'rgba(107,114,128,0.1)';

  return (
    <div className="screen-content p-8 max-w-4xl">
      <button onClick={() => navigate(-1)} className="mb-6 inline-flex items-center gap-2 text-sm transition hover:opacity-70" style={{ color: 'var(--text-secondary)' }}>
        <ArrowLeft className="w-4 h-4" />レポートに戻る
      </button>

      <div className="glass rounded-2xl p-6 mb-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 rounded-full blur-3xl" style={{ background: severityColor }} />
        <div className="relative">
          <div className="flex items-center gap-2 mb-3">
            <div className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-md ${severityClass} text-xs font-bold`}>
              <AlertOctagon className="w-3 h-3" />{severityLabels[severity]}
            </div>
            {resolved && (
              <div className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-bold" style={{ background: 'rgba(22,163,74,0.2)', color: '#16A34A', border: '1px solid rgba(22,163,74,0.3)' }}>
                <CheckCircle className="w-3 h-3" />対応済み
              </div>
            )}
          </div>
          <h1 className="text-2xl font-bold">{finding.title}</h1>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        <div className="glass rounded-xl p-4">
          <div className="text-xs mb-2 flex items-center gap-1" style={{ color: 'var(--text-tertiary)' }}><File className="w-3 h-3" />ファイル</div>
          <div className="font-mono text-sm">
            {finding.filePath || 'N/A'}
            {finding.lineStart && <span style={{ color: 'var(--text-tertiary)' }}>:{finding.lineStart}</span>}
          </div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-xs mb-2 flex items-center gap-1" style={{ color: 'var(--text-tertiary)' }}><Search className="w-3 h-3" />検出元</div>
          <div className="text-sm">
            {finding.agentSource || 'Unknown'}
            <div className="text-xs mt-0.5" style={{ color: 'var(--text-tertiary)' }}>AI評価</div>
          </div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-xs mb-2 flex items-center gap-1" style={{ color: 'var(--text-tertiary)' }}><BookOpen className="w-3 h-3" />該当基準</div>
          <div className="text-sm font-mono">
            {finding.asvsRequirementIds?.[0] || 'N/A'}
            {finding.cweIds?.[0] && <div className="text-xs mt-0.5" style={{ color: 'var(--text-tertiary)' }}>CWE-{finding.cweIds[0]}</div>}
          </div>
        </div>
      </div>

      {finding.detectedCode && (
        <section className="mb-6">
          <div className="flex items-center gap-2 mb-3"><div className="w-1 h-5 rounded" style={{ background: '#E11D48' }} /><h2 className="font-semibold flex items-center gap-2"><X className="w-4 h-4" style={{ color: '#E11D48' }} />検出されたコード</h2></div>
          <div className="glass rounded-xl overflow-hidden">
            <pre className="code-block p-5 overflow-x-auto" style={{ background: 'var(--code-bg)' }}><code>{finding.detectedCode}</code></pre>
          </div>
        </section>
      )}

      <section className="mb-6">
        <div className="flex items-center gap-2 mb-3"><div className="w-1 h-5 rounded" style={{ background: 'var(--accent-purple)' }} /><h2 className="font-semibold flex items-center gap-2"><Sparkles className="w-4 h-4" style={{ color: 'var(--accent-purple)' }} />AI による解説</h2></div>
        <div className="rounded-xl p-5" style={{ background: 'linear-gradient(135deg, rgba(167,139,250,0.08), rgba(79,139,255,0.08))', border: '1px solid rgba(167,139,250,0.2)' }}>
          <p className="leading-relaxed">{finding.description}</p>
        </div>
      </section>

      {finding.fixSuggestion && (
        <section className="mb-6">
          <div className="flex items-center gap-2 mb-3"><div className="w-1 h-5 rounded" style={{ background: '#16A34A' }} /><h2 className="font-semibold flex items-center gap-2"><CheckCircle className="w-4 h-4" style={{ color: '#16A34A' }} />修正案</h2></div>
          <div className="glass rounded-xl overflow-hidden relative">
            <div className="px-4 py-2 border-b flex items-center justify-between" style={{ borderColor: 'var(--border)', background: 'var(--bg-elevated)' }}>
              <span className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>{finding.filePath || 'suggestion'}</span>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(finding.fixSuggestion || '');
                  showToast('修正案をコピーしました', 'success');
                }}
                className="text-xs px-2 py-1 rounded transition hover:opacity-70 inline-flex items-center gap-1.5"
                style={{ background: 'var(--border)', color: 'var(--text-secondary)' }}
              >
                <Copy className="w-3 h-3" />コピー
              </button>
            </div>
            <pre className="code-block p-5 overflow-x-auto" style={{ background: 'var(--code-bg)' }}><code>{finding.fixSuggestion}</code></pre>
          </div>
        </section>
      )}

      {finding.references && finding.references.length > 0 && (
        <section className="glass rounded-xl p-5 mb-6">
          <div className="flex items-center gap-2 mb-3"><BookMarked className="w-4 h-4" style={{ color: 'var(--accent-cyan)' }} /><h3 className="font-semibold">参考リンク</h3></div>
          <ul className="space-y-2 text-sm">
            {finding.references.map((ref, idx) => (
              <li key={idx}>
                <a href={ref.url} target="_blank" rel="noopener noreferrer" className="hover:underline" style={{ color: 'var(--accent-blue)' }}>{ref.title}</a>
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="flex justify-between items-center mb-6">
        <button
          onClick={handleToggleResolved}
          disabled={isUpdating}
          className="px-4 py-2 rounded-lg transition hover:opacity-80 text-sm inline-flex items-center gap-2 disabled:opacity-50"
          style={resolved ? { background: 'var(--bg-elevated)', color: 'var(--text-secondary)', border: '1px solid var(--border)' } : { background: 'rgba(22,163,74,0.2)', color: '#16A34A', border: '1px solid rgba(22,163,74,0.3)' }}
        >
          {isUpdating ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : resolved ? (
            <Undo2 className="w-4 h-4" />
          ) : (
            <CheckCircle className="w-4 h-4" />
          )}
          {resolved ? '未対応に戻す' : '対応済みにする'}
        </button>
      </div>

      <div className="flex justify-between pt-6 border-t" style={{ borderColor: 'var(--border)' }}>
        <button className="px-5 py-2.5 rounded-xl border transition hover:opacity-80 text-sm inline-flex items-center gap-2" style={{ borderColor: 'var(--border)' }}>
          <ArrowLeft className="w-4 h-4" />前の指摘
        </button>
        <button className="px-5 py-2.5 rounded-xl border transition hover:opacity-80 text-sm inline-flex items-center gap-2" style={{ borderColor: 'var(--border)' }}>
          次の指摘<ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
