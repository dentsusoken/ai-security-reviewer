import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../../features/theme/ThemeProvider';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="theme-toggle"
      aria-label="テーマ切替"
    >
      <div className="theme-toggle-thumb">
        {theme === 'dark' ? (
          <Moon className="w-3 h-3" />
        ) : (
          <Sun className="w-3 h-3" />
        )}
      </div>
    </button>
  );
}
