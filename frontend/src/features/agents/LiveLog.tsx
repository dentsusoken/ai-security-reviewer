import { Terminal } from 'lucide-react';

interface LiveLogProps {
  lines: string[];
}

export function LiveLog({ lines }: LiveLogProps) {
  return (
    <div className="glass rounded-2xl overflow-hidden mb-6">
      <div
        className="px-5 py-3 border-b flex items-center justify-between"
        style={{ borderColor: 'var(--border)' }}
      >
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4" style={{ color: 'var(--text-tertiary)' }} />
          <span
            className="text-xs font-semibold uppercase tracking-wider"
            style={{ color: 'var(--text-secondary)' }}
          >
            Live Log
          </span>
        </div>
        <div className="flex gap-1.5">
          <span
            className="w-2.5 h-2.5 rounded-full"
            style={{ background: 'rgba(239,68,68,0.5)' }}
          />
          <span
            className="w-2.5 h-2.5 rounded-full"
            style={{ background: 'rgba(234,179,8,0.5)' }}
          />
          <span
            className="w-2.5 h-2.5 rounded-full"
            style={{ background: 'rgba(34,197,94,0.5)' }}
          />
        </div>
      </div>

      <div
        className="p-5 code-block max-h-48 overflow-y-auto space-y-1 font-mono text-sm"
        style={{ background: 'var(--code-bg)' }}
      >
        {lines.map((line) => (
          <div key={line}>{line}</div>
        ))}
        <div className="animate-pulse" style={{ color: 'var(--accent-blue)' }}>
          ▊
        </div>
      </div>
    </div>
  );
}
