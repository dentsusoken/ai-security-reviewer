import { BookOpen, ChevronRight, File } from 'lucide-react';
import { SeverityBadge } from './SeverityBadge';

export interface FindingItem {
  id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  file: string;
  standard: string;
}

interface FindingCardProps {
  finding: FindingItem;
  onClick: (findingId: string) => void;
}

const borderColors = {
  CRITICAL: '#E11D48',
  HIGH: '#EA580C',
  MEDIUM: '#CA8A04',
  LOW: '#16A34A',
};

export function FindingCard({ finding, onClick }: FindingCardProps) {
  return (
    <button
      type="button"
      onClick={() => onClick(finding.id)}
      className="glass rounded-2xl p-5 cursor-pointer transition group w-full text-left"
      style={{ borderLeft: `3px solid ${borderColors[finding.severity]}` }}
    >
      <div className="flex items-start gap-4">
        <SeverityBadge severity={finding.severity} />
        <div className="flex-1">
          <div className="font-semibold mb-1.5">{finding.title}</div>
          <div
            className="flex items-center gap-3 text-xs font-mono flex-wrap"
            style={{ color: 'var(--text-tertiary)' }}
          >
            <span className="flex items-center gap-1">
              <File className="w-3 h-3" />
              {finding.file}
            </span>
            <span className="flex items-center gap-1">
              <BookOpen className="w-3 h-3" />
              {finding.standard}
            </span>
          </div>
        </div>
        <ChevronRight className="w-5 h-5" style={{ color: 'var(--text-tertiary)' }} />
      </div>
    </button>
  );
}
