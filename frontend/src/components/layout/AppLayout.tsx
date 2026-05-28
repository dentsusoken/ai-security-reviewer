import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export function AppLayout() {
  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg-base)' }}>
      <Header />
      <div className="app-body flex flex-1">
        <button
          type="button"
          aria-label="サイドバーを閉じる"
          className="app-sidebar-overlay"
          onClick={() => document.body.classList.remove('sidebar-open')}
        />
        <Sidebar />
        <main className="app-main flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
