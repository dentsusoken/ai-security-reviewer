import { FolderGit2, Code2, Globe } from 'lucide-react';

export type ReviewType = 'github' | 'code' | 'url';

interface ReviewTypeSelectorProps {
  value: ReviewType;
  onChange: (value: ReviewType) => void;
}

const options: Array<{
  value: ReviewType;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
}> = [
  { value: 'github', title: 'GitHub', description: 'リポジトリURL', icon: FolderGit2 },
  { value: 'code', title: 'コード', description: '直接貼り付け', icon: Code2 },
  { value: 'url', title: 'URL', description: '動的スキャン', icon: Globe },
];

export function ReviewTypeSelector({ value, onChange }: ReviewTypeSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
      {options.map((option) => {
        const selected = value === option.value;
        const Icon = option.icon;

        return (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className="rounded-xl border p-4 text-left transition"
            style={{
              borderColor: selected ? 'var(--accent-blue)' : 'var(--border)',
              background: selected ? 'rgba(79, 139, 255, 0.10)' : 'transparent',
              minHeight: 110,
            }}
          >
            <Icon className="w-5 h-5 mb-2" style={{ color: 'var(--text-secondary)' }} />
            <div className="font-semibold text-sm">{option.title}</div>
            <div className="text-xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
              {option.description}
            </div>
          </button>
        );
      })}
    </div>
  );
}
