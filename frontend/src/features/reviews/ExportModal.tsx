import { Download, FileSpreadsheet, FileText, FileJson, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { Modal } from '../../components/ui/Modal';
import { exportsApi } from '../../services/api';

type ExportFormat = 'excel' | 'markdown' | 'pdf' | 'json';

interface ExportModalProps {
  open: boolean;
  onClose: () => void;
  reviewId: string;
}

const FORMAT_OPTIONS: {
  id: ExportFormat;
  label: string;
  icon: React.ReactNode;
  available: boolean;
}[] = [
  { id: 'excel', label: 'Excel', icon: <FileSpreadsheet className="w-4 h-4" />, available: true },
  { id: 'markdown', label: 'Markdown', icon: <FileText className="w-4 h-4" />, available: false },
  { id: 'pdf', label: 'PDF', icon: <FileText className="w-4 h-4" />, available: false },
  { id: 'json', label: 'JSON', icon: <FileJson className="w-4 h-4" />, available: false },
];

export function ExportModal({ open, onClose, reviewId }: ExportModalProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('excel');
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async () => {
    if (selectedFormat !== 'excel') {
      setError('この形式はまだ実装されていません');
      return;
    }

    setIsDownloading(true);
    setError(null);

    try {
      await exportsApi.downloadExcel(reviewId);
      onClose();
    } catch (err) {
      console.error('Export failed:', err);
      setError('エクスポートに失敗しました。もう一度お試しください。');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="レポートをエクスポート"
      icon={<Download className="w-5 h-5" style={{ color: 'var(--accent-blue)' }} />}
      footer={
        <>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border transition hover:opacity-80 text-sm"
            style={{ borderColor: 'var(--border)' }}
            disabled={isDownloading}
          >
            キャンセル
          </button>
          <button
            onClick={handleDownload}
            className="btn-gradient px-4 py-2 rounded-lg font-semibold text-sm inline-flex items-center gap-2"
            disabled={
              isDownloading || !FORMAT_OPTIONS.find((f) => f.id === selectedFormat)?.available
            }
          >
            {isDownloading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                ダウンロード中...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                ダウンロード
              </>
            )}
          </button>
        </>
      }
    >
      <h3
        className="text-xs font-semibold uppercase tracking-wider mb-3"
        style={{ color: 'var(--text-secondary)' }}
      >
        出力形式
      </h3>
      <div className="grid grid-cols-4 gap-2 mb-6">
        {FORMAT_OPTIONS.map((format) => (
          <label
            key={format.id}
            className={`cursor-pointer ${!format.available ? 'opacity-50' : ''}`}
          >
            <input
              type="radio"
              name="format"
              checked={selectedFormat === format.id}
              onChange={() => setSelectedFormat(format.id)}
              disabled={!format.available}
              className="peer sr-only"
            />
            <div
              className="rounded-xl border p-3 text-center transition peer-checked:bg-blue-500/10 peer-checked:border-blue-400"
              style={{ borderColor: 'var(--border)' }}
            >
              <div className="flex justify-center mb-1">{format.icon}</div>
              <div className="text-xs font-semibold">{format.label}</div>
              {!format.available && (
                <div className="text-[10px] mt-1" style={{ color: 'var(--text-tertiary)' }}>
                  準備中
                </div>
              )}
            </div>
          </label>
        ))}
      </div>

      {selectedFormat === 'excel' && (
        <div className="mb-4 p-3 rounded-lg" style={{ background: 'var(--bg-elevated)' }}>
          <h4 className="text-xs font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>
            Excel ファイルの内容
          </h4>
          <ul className="text-xs space-y-1" style={{ color: 'var(--text-tertiary)' }}>
            <li>📊 サマリー（基本情報、スコア、重要度別件数）</li>
            <li>📋 指摘事項一覧（表形式、フィルター可能）</li>
            <li>📝 詳細（各指摘の説明、コード、修正案）</li>
          </ul>
        </div>
      )}

      {error && (
        <div
          className="mb-4 p-3 rounded-lg text-sm"
          style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)' }}
        >
          {error}
        </div>
      )}

      <h3
        className="text-xs font-semibold uppercase tracking-wider mb-3"
        style={{ color: 'var(--text-secondary)' }}
      >
        含める内容
      </h3>
      <div className="space-y-2">
        {['サマリー', '観点別評価', '全指摘事項', '修正案コード'].map((item) => (
          <label
            key={item}
            className="flex items-center gap-3 cursor-pointer p-2 rounded-lg hover:opacity-80"
          >
            <input type="checkbox" defaultChecked style={{ accentColor: 'var(--accent-blue)' }} />
            <span className="text-sm">{item}</span>
          </label>
        ))}
      </div>
    </Modal>
  );
}
