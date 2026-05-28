import { CheckCircle2, Info, XCircle } from 'lucide-react';

export type ToastType = 'success' | 'info' | 'error';

export interface ToastMessage {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastProps {
  toast: ToastMessage;
}

export function Toast({ toast }: ToastProps) {
  const styles = {
    success: {
      bg: 'rgba(22,163,74,0.15)',
      color: '#16A34A',
      border: '1px solid rgba(22,163,74,0.4)',
      icon: <CheckCircle2 className="w-4 h-4" />,
    },
    info: {
      bg: 'rgba(79,139,255,0.15)',
      color: 'var(--accent-blue)',
      border: '1px solid rgba(79,139,255,0.4)',
      icon: <Info className="w-4 h-4" />,
    },
    error: {
      bg: 'rgba(225,29,72,0.15)',
      color: '#E11D48',
      border: '1px solid rgba(225,29,72,0.4)',
      icon: <XCircle className="w-4 h-4" />,
    },
  }[toast.type];

  return (
    <div
      className="glass-strong rounded-xl px-4 py-3 flex items-center gap-2 text-sm font-semibold fade-in-up"
      style={{ background: styles.bg, color: styles.color, border: styles.border }}
      role="status"
    >
      {styles.icon}
      <span>{toast.message}</span>
    </div>
  );
}
