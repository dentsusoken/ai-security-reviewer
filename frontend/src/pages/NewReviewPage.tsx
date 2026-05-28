import { AlertTriangle, Gauge, Layers, Loader2, Play, PlusCircle, Zap } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CodeInputForm } from '../features/reviews/CodeInputForm';
import { GitHubInputForm } from '../features/reviews/GitHubInputForm';
import { ReviewTypeSelector, type ReviewType } from '../features/reviews/ReviewTypeSelector';
import { UrlScanForm } from '../features/reviews/UrlScanForm';
import { reviewsApi } from '../services/api';
import type { ReviewCreateRequest, Perspective, ReviewDepth as ApiReviewDepth } from '../types/api';

type ReviewDepth = 'quick' | 'standard' | 'detailed';

export function NewReviewPage() {
  const navigate = useNavigate();
  const [reviewType, setReviewType] = useState<ReviewType>('github');
  const [depth, setDepth] = useState<ReviewDepth>('standard');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [githubData, setGithubData] = useState({
    repoUrl: '',
    branch: 'main',
  });

  const [codeData, setCodeData] = useState({
    fileName: '',
    language: 'auto',
    sourceCode: '',
  });

  const [urlData, setUrlData] = useState({
    targetUrl: '',
    verifyMethod: 'meta' as 'meta' | 'dns',
    scanType: 'baseline' as 'baseline' | 'full',
  });

  const [aspects, setAspects] = useState({
    asvs: true,
    sast: true,
    dast: false,
  });

  const canStart =
    !isSubmitting &&
    ((reviewType === 'github' && githubData.repoUrl.trim().length > 0) ||
      (reviewType === 'code' && codeData.sourceCode.trim().length > 0) ||
      (reviewType === 'url' && urlData.targetUrl.trim().length > 0));

  const handleStartReview = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      // Build perspectives array
      const perspectives: Perspective[] = [];
      if (aspects.asvs) perspectives.push('asvs');
      if (aspects.sast) perspectives.push('sast');
      if (aspects.dast) perspectives.push('dast');

      // Build request based on review type
      const request: ReviewCreateRequest = {
        inputType: reviewType,
        perspectives,
        depth: depth as ApiReviewDepth,
      };

      if (reviewType === 'github') {
        request.repoUrl = githubData.repoUrl;
        request.branch = githubData.branch;
      } else if (reviewType === 'code') {
        request.code = codeData.sourceCode;
        request.filename = codeData.fileName || undefined;
        request.language = codeData.language !== 'auto' ? codeData.language : undefined;
      } else if (reviewType === 'url') {
        request.targetUrl = urlData.targetUrl;
      }

      const response = await reviewsApi.create(request);

      // Navigate to progress page with the new review ID and repo info
      navigate(`/reviews/${response.reviewSessionId}/progress`, {
        state: {
          repoUrl: reviewType === 'github' ? githubData.repoUrl : undefined,
          branch: reviewType === 'github' ? githubData.branch : undefined,
        },
      });
    } catch (err) {
      console.error('Failed to create review:', err);
      setError('レビューの作成に失敗しました。もう一度お試しください。');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="screen-content p-8 max-w-3xl">
      <div className="mb-6">
        <div
          className="flex items-center gap-2 text-xs mb-2"
          style={{ color: 'var(--text-tertiary)' }}
        >
          <PlusCircle className="w-3 h-3" />
          <span>NEW REVIEW</span>
        </div>
        <h1 className="text-3xl font-bold">新規セキュリティレビュー</h1>
        <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
          AIエージェントがコードを多角的に分析します
        </p>
      </div>

      <div className="glass rounded-2xl p-6 mb-5">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="w-4 h-4" style={{ color: 'var(--accent-blue)' }} />
          <h2 className="font-semibold">レビュー対象タイプ</h2>
        </div>
        <ReviewTypeSelector value={reviewType} onChange={setReviewType} />
      </div>

      {reviewType === 'github' ? (
        <GitHubInputForm
          repoUrl={githubData.repoUrl}
          branch={githubData.branch}
          onChange={(field, value) => setGithubData((prev) => ({ ...prev, [field]: value }))}
        />
      ) : null}

      {reviewType === 'code' ? (
        <CodeInputForm
          fileName={codeData.fileName}
          language={codeData.language}
          sourceCode={codeData.sourceCode}
          onChange={(field, value) => setCodeData((prev) => ({ ...prev, [field]: value }))}
        />
      ) : null}

      {reviewType === 'url' ? (
        <UrlScanForm
          targetUrl={urlData.targetUrl}
          verifyMethod={urlData.verifyMethod}
          scanType={urlData.scanType}
          onChange={(field, value) =>
            setUrlData((prev) => ({
              ...prev,
              [field]: value as 'meta' | 'dns' | 'baseline' | 'full',
            }))
          }
        />
      ) : null}

      <div className="glass rounded-2xl p-6 mb-5">
        <div className="flex items-center gap-2 mb-4">
          <Layers className="w-4 h-4" style={{ color: 'var(--accent-cyan)' }} />
          <h2 className="font-semibold">
            レビュー観点{' '}
            <span className="text-xs font-normal" style={{ color: 'var(--text-tertiary)' }}>
              (複数選択可)
            </span>
          </h2>
        </div>

        <div className="space-y-3">
          <label
            className="flex items-start gap-3 cursor-pointer p-3 rounded-xl border transition"
            style={{ borderColor: 'var(--border)' }}
          >
            <input
              type="checkbox"
              checked={aspects.asvs}
              onChange={(e) => setAspects((prev) => ({ ...prev, asvs: e.target.checked }))}
              className="mt-1"
              style={{ accentColor: 'var(--accent-blue)' }}
            />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">OWASP ASVS 網羅性チェック</span>
                <span
                  className="text-xs px-2 py-0.5 rounded"
                  style={{ background: 'rgba(79,139,255,0.2)', color: 'var(--accent-blue)' }}
                >
                  推奨
                </span>
              </div>
              <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
                AIエージェントが仕様観点でレビュー
              </div>
            </div>
          </label>

          <label
            className="flex items-start gap-3 cursor-pointer p-3 rounded-xl border transition"
            style={{ borderColor: 'var(--border)' }}
          >
            <input
              type="checkbox"
              checked={aspects.sast}
              onChange={(e) => setAspects((prev) => ({ ...prev, sast: e.target.checked }))}
              className="mt-1"
              style={{ accentColor: 'var(--accent-blue)' }}
            />
            <div className="flex-1">
              <div className="font-semibold text-sm">静的解析 (Semgrep)</div>
              <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
                既知の脆弱性パターンをコード検索
              </div>
            </div>
          </label>

          <label
            className="flex items-start gap-3 cursor-pointer p-3 rounded-xl border transition"
            style={{ borderColor: 'var(--border)' }}
          >
            <input
              type="checkbox"
              checked={aspects.dast}
              onChange={(e) => setAspects((prev) => ({ ...prev, dast: e.target.checked }))}
              className="mt-1"
              style={{ accentColor: 'var(--accent-blue)' }}
            />
            <div className="flex-1">
              <div className="font-semibold text-sm">動的スキャン (OWASP ZAP)</div>
              <div className="text-xs mt-1 flex items-center gap-1" style={{ color: '#EA580C' }}>
                <AlertTriangle className="w-3 h-3" />
                URL所有確認が必要
              </div>
            </div>
          </label>
        </div>
      </div>

      <div className="glass rounded-2xl p-6 mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Gauge className="w-4 h-4" style={{ color: 'var(--accent-purple)' }} />
          <h2 className="font-semibold">レビュー深度</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            { value: 'quick' as const, title: 'クイック', eta: '〜5分' },
            { value: 'standard' as const, title: '標準', eta: '〜10分', recommended: true },
            { value: 'detailed' as const, title: '詳細', eta: '〜20分' },
          ].map((item) => {
            const selected = depth === item.value;
            return (
              <button
                key={item.value}
                type="button"
                onClick={() => setDepth(item.value)}
                className="rounded-xl border p-4 transition text-center relative"
                style={{
                  borderColor: selected ? 'var(--accent-purple)' : 'var(--border)',
                  background: selected ? 'rgba(167,139,250,0.1)' : 'transparent',
                }}
              >
                {item.recommended ? (
                  <span
                    className="absolute -top-2 -right-2 text-xs px-2 py-0.5 rounded-full text-white"
                    style={{
                      background:
                        'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
                    }}
                  >
                    推奨
                  </span>
                ) : null}
                <div className="font-semibold text-sm">{item.title}</div>
                <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
                  {item.eta}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex justify-end gap-3">
        {error && (
          <div className="flex-1 text-sm text-red-500 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            {error}
          </div>
        )}
        <button
          onClick={() => navigate('/dashboard')}
          className="px-6 py-3 rounded-xl border transition hover:opacity-80"
          style={{ borderColor: 'var(--border)' }}
        >
          キャンセル
        </button>
        <button
          onClick={handleStartReview}
          disabled={!canStart}
          className="btn-gradient px-6 py-3 rounded-xl font-semibold inline-flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              作成中...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              レビューを開始
            </>
          )}
        </button>
      </div>
    </div>
  );
}
