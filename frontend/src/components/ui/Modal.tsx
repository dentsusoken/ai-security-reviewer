import type { ReactNode } from 'react';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  icon?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
}

export function Modal({ open, onClose, title, icon, children, footer }: ModalProps) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-40 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)' }}
      onClick={onClose}
    >
      <div
        className="modal-panel glass-strong rounded-2xl w-full overflow-hidden glow-blue flex flex-col"
        style={{ maxWidth: '32rem', maxHeight: '90vh' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center p-5 border-b" style={{ borderColor: 'var(--border)' }}>
          <div className="flex items-center gap-2">
            {icon}
            <h2 className="font-bold">{title}</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center transition hover:opacity-70"
            style={{ color: 'var(--text-secondary)' }}
            aria-label="モーダルを閉じる"
          >
            x
          </button>
        </div>

        <div className="p-5 overflow-y-auto flex-1">{children}</div>

        {footer ? (
          <div className="flex justify-end gap-2 p-5 border-t" style={{ borderColor: 'var(--border)' }}>
            {footer}
          </div>
        ) : null}
      </div>
    </div>
  );
}
