import { ArrowUpDown, Filter, ListChecks } from 'lucide-react';
import { FindingCard, type FindingItem } from './FindingCard';

interface FindingsListProps {
  findings: FindingItem[];
  onSelect: (findingId: string) => void;
}

export function FindingsList({ findings, onSelect }: FindingsListProps) {
  return (
    <>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ListChecks className="w-4 h-4" style={{ color: 'var(--text-tertiary)' }} />
          <h2
            className="text-sm font-semibold uppercase tracking-wider"
            style={{ color: 'var(--text-secondary)' }}
          >
            指摘事項一覧
          </h2>
          <span
            className="text-xs px-2 py-0.5 rounded-full font-mono"
            style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)' }}
          >
            {findings.length}件
          </span>
        </div>
        <div className="flex gap-2">
          <button
            className="text-xs px-3 py-1.5 rounded-lg border transition hover:opacity-80 inline-flex items-center gap-1.5"
            style={{ borderColor: 'var(--border)' }}
          >
            <Filter className="w-3 h-3" />
            絞り込み
          </button>
          <button
            className="text-xs px-3 py-1.5 rounded-lg border transition hover:opacity-80 inline-flex items-center gap-1.5"
            style={{ borderColor: 'var(--border)' }}
          >
            <ArrowUpDown className="w-3 h-3" />
            並替
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {findings.map((finding) => (
          <FindingCard key={finding.id} finding={finding} onClick={onSelect} />
        ))}
      </div>
    </>
  );
}
