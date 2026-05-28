import { useState } from 'react';
import { PanelLeft, LogOut, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ThemeToggle } from '../ui/ThemeToggle';

export function Header() {
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    navigate('/');
  };

  const toggleSidebar = () => {
    const nextOpen = !sidebarOpen;
    setSidebarOpen(nextOpen);

    // Mobile: slide drawer. Desktop: collapse to icon rail.
    if (window.innerWidth <= 1023) {
      document.body.classList.toggle('sidebar-open', nextOpen);
      return;
    }

    document.body.classList.remove('sidebar-open');
    document.body.classList.toggle('sidebar-collapsed', nextOpen);
  };

  return (
    <header className="glass border-b sticky top-0 z-30" style={{ borderColor: 'var(--border)' }}>
      <div className="px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={toggleSidebar}
            className="w-9 h-9 rounded-xl border transition hover:opacity-80 inline-flex items-center justify-center"
            style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}
            title="サイドバー切替"
          >
            <PanelLeft className="w-4 h-4" />
          </button>
          <div
            className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center glow-blue"
          >
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-base">AI Security Reviewer</div>
            <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
              Powered by Azure AI Agent Service
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center text-xs font-bold text-white">
              T
            </div>
            <div className="text-sm">テストユーザー</div>
          </div>
          <ThemeToggle />
          <button
            onClick={handleLogout}
            className="ml-2 px-3 py-1.5 rounded-lg border transition hover:opacity-80 text-xs inline-flex items-center gap-1.5"
            style={{ borderColor: 'var(--border)', color: 'var(--text-secondary)' }}
            title="ログアウト"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>ログアウト</span>
          </button>
        </div>
      </div>
    </header>
  );
}
