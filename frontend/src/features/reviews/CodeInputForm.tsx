import { ClipboardPaste, Code2, FileCode2 } from 'lucide-react';

interface CodeInputFormProps {
  fileName: string;
  language: string;
  sourceCode: string;
  onChange: (field: 'fileName' | 'language' | 'sourceCode', value: string) => void;
}

export function CodeInputForm({ fileName, language, sourceCode, onChange }: CodeInputFormProps) {
  return (
    <div className="glass rounded-2xl p-6 mb-5">
      <label className="flex items-center gap-2 text-sm font-semibold mb-3">
        <FileCode2 className="w-4 h-4" style={{ color: 'var(--accent-blue)' }} />
        ファイル名 <span className="text-xs font-normal" style={{ color: 'var(--text-tertiary)' }}>(任意)</span>
      </label>
      <input
        type="text"
        value={fileName}
        onChange={(e) => onChange('fileName', e.target.value)}
        placeholder="例: users.js"
        className="w-full rounded-xl px-4 py-3 font-mono text-sm transition mb-5"
      />

      <label className="flex items-center gap-2 text-sm font-semibold mb-3">
        <Code2 className="w-4 h-4" style={{ color: 'var(--accent-purple)' }} />
        言語
      </label>
      <select
        value={language}
        onChange={(e) => onChange('language', e.target.value)}
        className="w-full rounded-xl px-4 py-3 text-sm transition mb-5"
      >
        <option value="auto">自動判定</option>
        <option value="javascript">JavaScript</option>
        <option value="typescript">TypeScript</option>
        <option value="python">Python</option>
        <option value="java">Java</option>
        <option value="go">Go</option>
      </select>

      <label className="flex items-center gap-2 text-sm font-semibold mb-3">
        <ClipboardPaste className="w-4 h-4" style={{ color: 'var(--accent-cyan)' }} />
        ソースコード <span style={{ color: '#E11D48' }}>*</span>
      </label>
      <textarea
        rows={10}
        value={sourceCode}
        onChange={(e) => onChange('sourceCode', e.target.value)}
        placeholder="ここにレビューしたいコードを貼り付けてください..."
        className="w-full rounded-xl px-4 py-3 font-mono text-sm transition resize-y"
      />
      <p className="text-xs mt-2" style={{ color: 'var(--text-tertiary)' }}>
        最大10,000行までサポート
      </p>
    </div>
  );
}
