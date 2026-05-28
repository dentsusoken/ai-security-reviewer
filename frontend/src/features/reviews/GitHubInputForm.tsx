import { FolderGit2, GitBranch, Info, Link } from 'lucide-react';

interface GitHubInputFormProps {
  repoUrl: string;
  branch: string;
  onChange: (field: 'repoUrl' | 'branch', value: string) => void;
}

export function GitHubInputForm({ repoUrl, branch, onChange }: GitHubInputFormProps) {
  return (
    <div className="glass rounded-2xl p-6 mb-5">
      <label className="flex items-center gap-2 text-sm font-semibold mb-3">
        <Link className="w-4 h-4" style={{ color: 'var(--accent-blue)' }} />
        リポジトリURL <span style={{ color: '#E11D48' }}>*</span>
      </label>
      <div className="relative">
        <FolderGit2
          className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2"
          style={{ color: 'var(--text-tertiary)' }}
        />
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => onChange('repoUrl', e.target.value)}
          placeholder="https://github.com/owner/repository"
          className="w-full rounded-xl pl-11 pr-4 py-3 font-mono text-sm transition"
        />
      </div>
      <p className="text-xs mt-2 flex items-center gap-1" style={{ color: 'var(--text-tertiary)' }}>
        <Info className="w-3 h-3" /> パブリックなGitHubリポジトリURLを入力してください
      </p>

      <label className="flex items-center gap-2 text-sm font-semibold mb-3 mt-5">
        <GitBranch className="w-4 h-4" style={{ color: 'var(--accent-purple)' }} />
        ブランチ
      </label>
      <input
        type="text"
        value={branch}
        onChange={(e) => onChange('branch', e.target.value)}
        placeholder="main"
        className="w-full rounded-xl px-4 py-3 font-mono text-sm transition"
      />
    </div>
  );
}
