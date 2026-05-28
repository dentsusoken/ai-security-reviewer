import { Gauge, Layers, Play, RefreshCw } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Modal } from '../../components/ui/Modal';
import type { HistoryItem } from '../history/HistoryCard';

interface RereviewModalProps {
  open: boolean;
  onClose: () => void;
  target: HistoryItem | null;
  onExecute: () => void;
}

type ReviewDepth = 'quick' | 'standard' | 'detailed';

export function RereviewModal({ open, onClose, target, onExecute }: RereviewModalProps) {
  const [depth, setDepth] = useState<ReviewDepth>('standard');
  const [aspects, setAspects] = useState({ asvs: true, sast: true, dast: false });

  useEffect(() => {
    if (!target) return;
    setAspects({
      asvs: target.aspects.includes('asvs'),
      sast: target.aspects.includes('sast'),
      dast: target.aspects.includes('dast'),
    });
  }, [target]);

  const estimatedTime = useMemo(() => {
    if (depth === 'quick') return '5分';
    if (depth === 'detailed') return '20分';
    return '10分';
  }, [depth]);

  if (!target) return null;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="再レビューを実行"
      icon={<RefreshCw className="w-5 h-5" style={{ color: 'var(--accent-blue)' }} />}
      footer={(
        <>
          <button onClick={onClose} className="px-4 py-2 rounded-lg border transition hover:opacity-80 text-sm" style={{ borderColor: 'var(--border)' }}>
            キャンセル
          </button>
          <button
            onClick={onExecute}
            disabled={!aspects.asvs && !aspects.sast && !aspects.dast}
            className="btn-gradient px-4 py-2 rounded-lg font-semibold text-sm inline-flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Play className="w-4 h-4" />実行
          </button>
        </>
      )}
    >
      <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>以下の設定で再レビューを実行します。</p>

      <div className="space-y-3 mb-5">
        <div className="flex items-center gap-3 p-3 rounded-xl" style={{ background: 'var(--bg-elevated)' }}>
          <div className="flex-1">
            <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>リポジトリ</div>
            <div className="font-semibold text-sm flex items-center gap-2">
              <span>{target.repo}</span>
              <span className="text-xs px-2 py-0.5 rounded font-mono" style={{ background: 'var(--bg-base)', color: 'var(--text-tertiary)' }}>{target.branch}</span>
            </div>
          </div>
        </div>

        <div className="p-3 rounded-xl" style={{ background: 'var(--bg-elevated)' }}>
          <div className="flex items-center gap-2 mb-2"><Layers className="w-4 h-4" style={{ color: 'var(--accent-cyan)' }} />レビュー観点</div>
          <div className="space-y-1 text-sm">
            <label className="flex items-center gap-2 cursor-pointer"><input type="checkbox" checked={aspects.asvs} onChange={(e) => setAspects((prev) => ({ ...prev, asvs: e.target.checked }))} />OWASP ASVS</label>
            <label className="flex items-center gap-2 cursor-pointer"><input type="checkbox" checked={aspects.sast} onChange={(e) => setAspects((prev) => ({ ...prev, sast: e.target.checked }))} />静的解析 (Semgrep)</label>
            <label className="flex items-center gap-2 cursor-pointer"><input type="checkbox" checked={aspects.dast} onChange={(e) => setAspects((prev) => ({ ...prev, dast: e.target.checked }))} />動的スキャン (ZAP)</label>
          </div>
        </div>

        <div className="p-3 rounded-xl" style={{ background: 'var(--bg-elevated)' }}>
          <div className="flex items-center gap-2 mb-2"><Gauge className="w-4 h-4" style={{ color: 'var(--accent-purple)' }} />レビュー深度</div>
          <div className="grid grid-cols-3 gap-2 text-sm">
            <button type="button" onClick={() => setDepth('quick')} className="rounded-lg border px-2 py-1.5" style={{ borderColor: depth === 'quick' ? 'var(--accent-purple)' : 'var(--border)', background: depth === 'quick' ? 'rgba(167,139,250,0.12)' : 'transparent' }}>クイック</button>
            <button type="button" onClick={() => setDepth('standard')} className="rounded-lg border px-2 py-1.5" style={{ borderColor: depth === 'standard' ? 'var(--accent-purple)' : 'var(--border)', background: depth === 'standard' ? 'rgba(167,139,250,0.12)' : 'transparent' }}>標準</button>
            <button type="button" onClick={() => setDepth('detailed')} className="rounded-lg border px-2 py-1.5" style={{ borderColor: depth === 'detailed' ? 'var(--accent-purple)' : 'var(--border)', background: depth === 'detailed' ? 'rgba(167,139,250,0.12)' : 'transparent' }}>詳細</button>
          </div>
        </div>
      </div>

      <div className="rounded-xl p-3 flex items-start gap-2 text-sm" style={{ background: 'rgba(79,139,255,0.08)', border: '1px solid rgba(79,139,255,0.2)' }}>
        <span style={{ color: 'var(--text-secondary)' }}>
          実行には約 <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>{estimatedTime}</span> かかります
        </span>
      </div>
    </Modal>
  );
}
