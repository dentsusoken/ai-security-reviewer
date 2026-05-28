import { AlertCircle, Check, Loader2, Pause } from 'lucide-react';
import { ProgressBar } from '../../components/ui/ProgressBar';

export type AgentStatus = 'completed' | 'running' | 'waiting' | 'failed';

interface AgentStatusCardProps {
  title: string;
  description: string;
  status: AgentStatus;
  details?: string;
  progress?: number;
  chips?: string[];
}

export function AgentStatusCard({ title, description, status, details, progress, chips = [] }: AgentStatusCardProps) {
  if (status === 'completed') {
    return (
      <div className="glass rounded-2xl p-5 flex items-start gap-4">
        <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: 'rgba(22,163,74,0.2)' }}>
          <Check className="w-5 h-5" style={{ color: '#16A34A' }} />
        </div>
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <div>
              <div className="font-semibold">{title}</div>
              <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>{description}</div>
              {details ? <div className="text-xs mt-1 font-mono" style={{ color: 'var(--text-tertiary)' }}>{details}</div> : null}
              {chips.length ? (
                <div className="flex gap-2 mt-2 text-xs">
                  {chips.map((chip) => (
                    <span key={chip} className="px-2 py-0.5 rounded badge-medium">{chip}</span>
                  ))}
                </div>
              ) : null}
            </div>
            <span className="text-xs px-2 py-1 rounded-full font-semibold" style={{ background: 'rgba(22,163,74,0.2)', color: '#16A34A' }}>
              完了
            </span>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'running') {
    return (
      <div className="rounded-2xl p-5 flex items-start gap-4 pulse-glow" style={{ background: 'rgba(79,139,255,0.08)', border: '1px solid rgba(79,139,255,0.4)' }}>
        <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: 'rgba(79,139,255,0.2)' }}>
          <Loader2 className="w-5 h-5 spin-slow" style={{ color: 'var(--accent-blue)' }} />
        </div>
        <div className="flex-1">
          <div className="flex justify-between items-start mb-3">
            <div>
              <div className="font-semibold flex items-center gap-2">{title}
                <span className="text-xs px-2 py-0.5 rounded-full font-mono" style={{ background: 'rgba(79,139,255,0.2)', color: 'var(--accent-blue)' }}>
                  running
                </span>
              </div>
              <div className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>{description}</div>
            </div>
          </div>
          <ProgressBar value={progress ?? 0} showShimmer heightClassName="h-1.5" gradient="linear-gradient(90deg, var(--accent-blue), var(--accent-cyan))" />
          <div className="text-xs mt-1 font-mono" style={{ color: 'var(--text-tertiary)' }}>{progress ?? 0}%</div>
        </div>
      </div>
    );
  }

  if (status === 'failed') {
    return (
      <div className="rounded-2xl p-5 flex items-start gap-4" style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.4)' }}>
        <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: 'rgba(239,68,68,0.2)' }}>
          <AlertCircle className="w-5 h-5" style={{ color: '#EF4444' }} />
        </div>
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <div>
              <div className="font-semibold">{title}</div>
              <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>{description}</div>
              {details ? <div className="text-xs mt-1 font-mono" style={{ color: 'var(--text-tertiary)' }}>{details}</div> : null}
            </div>
            <span className="text-xs px-2 py-1 rounded-full font-semibold" style={{ background: 'rgba(239,68,68,0.2)', color: '#EF4444' }}>
              エラー
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl p-5 flex items-start gap-4 opacity-50" style={{ border: '1px solid var(--border)' }}>
      <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: 'var(--bg-elevated)' }}>
        <Pause className="w-5 h-5" style={{ color: 'var(--text-tertiary)' }} />
      </div>
      <div className="flex-1">
        <div className="flex justify-between items-start">
          <div>
            <div className="font-semibold" style={{ color: 'var(--text-secondary)' }}>{title}</div>
            <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>{description}</div>
          </div>
          <span className="text-xs px-2 py-1 rounded-full" style={{ background: 'var(--bg-elevated)', color: 'var(--text-tertiary)' }}>
            待機中
          </span>
        </div>
      </div>
    </div>
  );
}
