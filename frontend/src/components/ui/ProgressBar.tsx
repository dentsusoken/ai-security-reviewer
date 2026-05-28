interface ProgressBarProps {
  value: number;
  showShimmer?: boolean;
  gradient?: string;
  heightClassName?: string;
}

export function ProgressBar({
  value,
  showShimmer = false,
  gradient = 'linear-gradient(90deg, var(--accent-blue), var(--accent-purple), var(--accent-cyan))',
  heightClassName = 'h-2',
}: ProgressBarProps) {
  const normalized = Math.max(0, Math.min(100, value));

  return (
    <div className={`w-full ${heightClassName} rounded-full overflow-hidden relative`} style={{ background: 'var(--border)' }}>
      <div className="h-full rounded-full relative" style={{ width: `${normalized}%`, background: gradient }}>
        {showShimmer ? <div className="absolute inset-0 shimmer" /> : null}
      </div>
    </div>
  );
}
