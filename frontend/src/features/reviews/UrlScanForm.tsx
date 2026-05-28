import { AlertTriangle, CheckCircle2, Globe, Settings2, ShieldCheck } from 'lucide-react';

interface UrlScanFormProps {
  targetUrl: string;
  verifyMethod: 'meta' | 'dns';
  scanType: 'baseline' | 'full';
  onChange: (field: 'targetUrl' | 'verifyMethod' | 'scanType', value: string) => void;
}

export function UrlScanForm({ targetUrl, verifyMethod, scanType, onChange }: UrlScanFormProps) {
  return (
    <div className="glass rounded-2xl p-6 mb-5">
      <div
        className="rounded-xl p-4 mb-5 flex items-start gap-3"
        style={{ background: 'rgba(234,88,12,0.1)', border: '1px solid rgba(234,88,12,0.3)' }}
      >
        <AlertTriangle className="w-5 h-5 mt-0.5 shrink-0" style={{ color: '#EA580C' }} />
        <div className="text-sm">
          <div className="font-semibold mb-1" style={{ color: '#EA580C' }}>動的スキャンには所有確認が必要です</div>
          <div style={{ color: 'var(--text-secondary)' }}>
            他人のサイトへの無断スキャンは違法となる可能性があります。<br />
            必ずご自身が所有・管理するURLを指定してください。
          </div>
        </div>
      </div>

      <label className="flex items-center gap-2 text-sm font-semibold mb-3">
        <Globe className="w-4 h-4" style={{ color: 'var(--accent-blue)' }} />
        スキャン対象URL <span style={{ color: '#E11D48' }}>*</span>
      </label>
      <div className="relative">
        <Globe className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-tertiary)' }} />
        <input
          type="text"
          value={targetUrl}
          onChange={(e) => onChange('targetUrl', e.target.value)}
          placeholder="https://your-app.example.com"
          className="w-full rounded-xl pl-11 pr-4 py-3 font-mono text-sm transition"
        />
      </div>
      <p className="text-xs mt-2" style={{ color: 'var(--text-tertiary)' }}>
        💡 あなたが所有・管理する公開済みアプリのURLを入力してください
      </p>

      <label className="flex items-center gap-2 text-sm font-semibold mb-3 mt-5">
        <ShieldCheck className="w-4 h-4" style={{ color: 'var(--accent-purple)' }} />
        所有確認方式
      </label>
      <div className="space-y-2">
        <label className="cursor-pointer flex items-start gap-3 p-3 rounded-xl border transition" style={{ borderColor: 'var(--border)' }}>
          <input
            type="radio"
            name="verify-method"
            checked={verifyMethod === 'meta'}
            onChange={() => onChange('verifyMethod', 'meta')}
            className="mt-1"
          />
          <div>
            <div className="font-semibold text-sm">HTMLメタタグ</div>
            <div className="text-xs mt-1 mb-2" style={{ color: 'var(--text-tertiary)' }}>指定のメタタグをサイトの head に追加</div>
            <code className="text-xs px-2 py-1 rounded font-mono inline-block" style={{ background: 'var(--bg-elevated)', color: 'var(--accent-cyan)' }}>
              {'<meta name="ai-sec-verify" content="abc123xyz" />'}
            </code>
          </div>
        </label>

        <label className="cursor-pointer flex items-start gap-3 p-3 rounded-xl border transition" style={{ borderColor: 'var(--border)' }}>
          <input
            type="radio"
            name="verify-method"
            checked={verifyMethod === 'dns'}
            onChange={() => onChange('verifyMethod', 'dns')}
            className="mt-1"
          />
          <div>
            <div className="font-semibold text-sm">DNS TXTレコード</div>
            <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>ドメインの DNS に TXT レコードを追加</div>
          </div>
        </label>
      </div>

      <button
        type="button"
        className="mt-4 w-full px-4 py-2.5 rounded-xl border text-sm font-semibold transition inline-flex items-center justify-center gap-2 hover:opacity-80"
        style={{ borderColor: 'var(--accent-blue)', color: 'var(--accent-blue)' }}
      >
        <CheckCircle2 className="w-4 h-4" />所有確認を実行
      </button>

      <label className="flex items-center gap-2 text-sm font-semibold mb-3 mt-5">
        <Settings2 className="w-4 h-4" style={{ color: 'var(--accent-cyan)' }} />
        スキャンタイプ
      </label>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <label className="cursor-pointer">
          <input
            type="radio"
            name="scan-type"
            checked={scanType === 'baseline'}
            onChange={() => onChange('scanType', 'baseline')}
            className="peer sr-only"
          />
          <div
            className="rounded-xl border p-4 transition peer-checked:bg-blue-500/10 peer-checked:border-blue-400"
            style={{ borderColor: 'var(--border)' }}
          >
            <div className="font-semibold text-sm">Baseline Scan</div>
            <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>受動的・5分程度</div>
          </div>
        </label>

        <label className="cursor-pointer">
          <input
            type="radio"
            name="scan-type"
            checked={scanType === 'full'}
            onChange={() => onChange('scanType', 'full')}
            className="peer sr-only"
          />
          <div
            className="rounded-xl border p-4 transition peer-checked:bg-blue-500/10 peer-checked:border-blue-400"
            style={{ borderColor: 'var(--border)' }}
          >
            <div className="font-semibold text-sm">Full Scan</div>
            <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>能動的・20-30分</div>
          </div>
        </label>
      </div>
    </div>
  );
}
