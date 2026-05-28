import type { ReactNode } from 'react';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

export function GlassCard({ children, className = '', onClick }: GlassCardProps) {
  return (
    <div
      className={`glass rounded-2xl ${onClick ? 'cursor-pointer hover-row transition' : ''} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
}
