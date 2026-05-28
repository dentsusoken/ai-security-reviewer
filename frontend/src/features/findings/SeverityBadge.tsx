interface SeverityBadgeProps {
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
}

const styles = {
  CRITICAL: { className: 'badge-critical', border: '#E11D48' },
  HIGH: { className: 'badge-high', border: '#EA580C' },
  MEDIUM: { className: 'badge-medium', border: '#CA8A04' },
  LOW: { className: 'badge-low', border: '#16A34A' },
};

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  return (
    <span className={`text-xs font-bold px-2.5 py-1 rounded-md ${styles[severity].className} shrink-0`}>
      {severity}
    </span>
  );
}
