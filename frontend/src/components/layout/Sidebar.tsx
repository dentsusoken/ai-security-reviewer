import { LayoutDashboard, PlusCircle, History } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

export function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { label: 'ダッシュボード', path: '/dashboard', icon: LayoutDashboard },
    { label: '新規レビュー', path: '/reviews/new', icon: PlusCircle },
    { label: '履歴', path: '/history', icon: History },
  ];

  return (
    <aside
      className="app-sidebar border-r min-h-[calc(100vh-110px)] py-4"
      style={{
        borderColor: 'var(--border)',
        background: 'var(--glass-bg)',
      }}
    >
      <nav className="space-y-1 px-2">
        {navItems.map(({ label, path, icon: Icon }) => (
          <button
            key={path}
            onClick={() => {
              navigate(path);
              document.body.classList.remove('sidebar-open');
            }}
            className={`nav-item flex items-center gap-3 px-4 py-2.5 rounded-r-lg w-full text-sm transition ${
              location.pathname === path ? 'active' : ''
            }`}
          >
            <Icon className="w-4 h-4" />
            <span className="sidebar-label">{label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}
