import { Clock, FolderGit2, Timer } from 'lucide-react';

export interface HistoryItem {
  id: string;
  repo: string;
  branch: string;
  timestamp: string;
  duration: string;
  score: number;
  counts: string[];
  dateKey: 'today' | '7days' | '30days' | '90days' | 'older';
  aspects: Array<'asvs' | 'sast' | 'dast'>;
}

interface HistoryCardProps {
  item: HistoryItem;
  onOpen: (id: string) => void;
  onRereview: (item: HistoryItem) => void;
}

function scoreColor(score: number) {
  if (score >= 80) return '#16A34A';
  if (score >= 60) return '#CA8A04';
  if (score >= 40) return '#EA580C';
  return '#E11D48';
}

function tileBg(score: number) {
  if (score >= 80) return 'linear-gradient(135deg, rgba(22,163,74,0.2), rgba(8,145,178,0.2))';
  if (score >= 60) return 'linear-gradient(135deg, rgba(202,138,4,0.2), rgba(34,197,94,0.2))';
  if (score >= 40) return 'linear-gradient(135deg, rgba(234,88,12,0.2), rgba(225,29,72,0.2))';
  return 'linear-gradient(135deg, rgba(225,29,72,0.2), rgba(244,114,182,0.2))';
}

export function HistoryCard({ item, onOpen, onRereview }: HistoryCardProps) {
  const color = scoreColor(item.score);

  return (
    <div className="glass rounded-2xl p-5 transition">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-4 flex-1 min-w-[260px]">
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center"
            style={{ background: tileBg(item.score) }}
          >
            <FolderGit2 className="w-5 h-5" style={{ color }} />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-semibold">{item.repo}</span>
              <span
                className="text-xs px-2 py-0.5 rounded font-mono"
                style={{ background: 'var(--bg-elevated)', color: 'var(--text-tertiary)' }}
              >
                {item.branch}
              </span>
            </div>
            <div
              className="text-xs flex items-center gap-3 flex-wrap"
              style={{ color: 'var(--text-tertiary)' }}
            >
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {item.timestamp}
              </span>
              <span className="flex items-center gap-1">
                <Timer className="w-3 h-3" />
                {item.duration}
              </span>
              {item.counts.map((count) => (
                <span key={count}>{count}</span>
              ))}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-5">
          <div className="text-right">
            <div className="text-2xl font-bold" style={{ color }}>
              {item.score}
            </div>
            <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
              /100
            </div>
          </div>
          <div className="flex gap-1">
            <button
              onClick={() => onOpen(item.id)}
              className="px-3 py-1.5 rounded-lg border transition hover:opacity-80 text-xs"
              style={{ borderColor: 'var(--border)' }}
            >
              詳細
            </button>
            <button
              onClick={() => onRereview(item)}
              className="px-3 py-1.5 rounded-lg border transition hover:opacity-80 text-xs"
              style={{ borderColor: 'var(--border)' }}
            >
              再レビュー
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
