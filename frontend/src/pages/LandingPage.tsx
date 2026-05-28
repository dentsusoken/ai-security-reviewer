import { useNavigate } from 'react-router-dom';
import { FileSearch, Bot, ScanLine, Radar, ArrowRight } from 'lucide-react';
import { useAuth } from '../features/auth';

export function LandingPage() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();

  const handleSignIn = async () => {
    try {
      await login();
      navigate('/dashboard');
    } catch (error) {
      console.error('Sign in failed:', error);
      // In dev mode, login succeeds immediately
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center px-4 overflow-hidden" style={{ background: 'var(--bg-base)' }}>
      <div className="aurora"></div>
      <div className="relative z-10 max-w-2xl w-full text-center">
        {/* Status Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass mb-8 text-xs">
          <span className="relative flex w-2 h-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-400"></span>
          </span>
          <span style={{ color: 'var(--text-secondary)' }}>Powered by Azure AI Agent Service</span>
        </div>

        {/* Main Title */}
        <h1 className="text-6xl font-extrabold mb-6 tracking-tight leading-tight">
          <span className="gradient-text">AI Security</span>
          <br />
          <span style={{ color: 'var(--text-primary)' }}>Reviewer</span>
        </h1>

        {/* Subtitle */}
        <p className="text-lg mb-10 leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          SDDで開発したWebアプリを
          <br />
          <span style={{ color: 'var(--text-primary)' }} className="font-semibold">
            AIエージェント
          </span>
          が自動でレビュー
        </p>

        {/* Sign In Button */}
        <button
          onClick={handleSignIn}
          disabled={isLoading}
          className="btn-gradient px-8 py-4 rounded-xl font-semibold text-base inline-flex items-center gap-3 mb-12 hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg width="20" height="20" viewBox="0 0 21 21">
            <rect x="1" y="1" width="9" height="9" fill="#f25022" />
            <rect x="11" y="1" width="9" height="9" fill="#7fba00" />
            <rect x="1" y="11" width="9" height="9" fill="#00a4ef" />
            <rect x="11" y="11" width="9" height="9" fill="#ffb900" />
          </svg>
          {isLoading ? 'サインイン中...' : 'Microsoftでサインイン'}
          {!isLoading && <ArrowRight className="w-4 h-4" />}
        </button>

        {/* Feature Cards */}
        <div className="grid grid-cols-2 gap-4 mt-8">
          <div className="glass rounded-2xl p-5 text-left transition hover:scale-105" style={{ cursor: 'pointer' }}>
            <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style={{ background: 'rgba(79,139,255,0.2)' }}>
              <FileSearch className="w-5 h-5" style={{ color: 'var(--accent-blue)' }} />
            </div>
            <div className="font-semibold mb-1">OWASP ASVS 網羅性チェック</div>
            <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>AIエージェントが仕様観点で評価</div>
          </div>

          <div className="glass rounded-2xl p-5 text-left transition hover:scale-105" style={{ cursor: 'pointer' }}>
            <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style={{ background: 'rgba(167,139,250,0.2)' }}>
              <Bot className="w-5 h-5" style={{ color: 'var(--accent-purple)' }} />
            </div>
            <div className="font-semibold mb-1">AI コードレビュー</div>
            <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>根拠と修正案を自動提示</div>
          </div>

          <div className="glass rounded-2xl p-5 text-left transition hover:scale-105" style={{ cursor: 'pointer' }}>
            <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style={{ background: 'rgba(34,211,238,0.2)' }}>
              <ScanLine className="w-5 h-5" style={{ color: 'var(--accent-cyan)' }} />
            </div>
            <div className="font-semibold mb-1">静的解析 (Semgrep)</div>
            <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>既知の脆弱性パターンを検出</div>
          </div>

          <div className="glass rounded-2xl p-5 text-left transition hover:scale-105" style={{ cursor: 'pointer' }}>
            <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style={{ background: 'rgba(244,114,182,0.2)' }}>
              <Radar className="w-5 h-5" style={{ color: '#F472B6' }} />
            </div>
            <div className="font-semibold mb-1">動的スキャン (ZAP)</div>
            <div className="text-xs" style={{ color: 'var(--text-tertiary)' }}>所有確認済URLに対して実行</div>
          </div>
        </div>
      </div>
    </div>
  );
}
