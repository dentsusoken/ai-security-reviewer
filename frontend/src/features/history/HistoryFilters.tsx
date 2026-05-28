import { Calendar, Layers, Search, X } from 'lucide-react';
import { Dropdown } from '../../components/ui/Dropdown';

export interface HistoryFilterState {
  search: string;
  period: 'all' | 'today' | '7days' | '30days' | '90days';
  score: 'all' | 'excellent' | 'good' | 'warning' | 'danger';
  aspect: 'all' | 'asvs' | 'sast' | 'dast';
}

interface HistoryFiltersProps {
  value: HistoryFilterState;
  onChange: (next: HistoryFilterState) => void;
  onClear: () => void;
  isFiltered: boolean;
}

export function HistoryFilters({ value, onChange, onClear, isFiltered }: HistoryFiltersProps) {
  return (
    <>
      <div className="relative mb-4">
        <Search
          className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2"
          style={{ color: 'var(--text-tertiary)' }}
        />
        <input
          type="text"
          value={value.search}
          placeholder="リポジトリ名で検索..."
          onChange={(e) => onChange({ ...value, search: e.target.value })}
          className="w-full rounded-xl pl-11 pr-4 py-3 text-sm transition"
        />
      </div>

      <div className="flex gap-2 mb-4 text-sm flex-wrap items-center">
        <Dropdown
          label="期間"
          icon={<Calendar className="w-3 h-3" />}
          value={value.period}
          onChange={(period) =>
            onChange({ ...value, period: period as HistoryFilterState['period'] })
          }
          options={[
            { value: 'all', label: '全期間' },
            { value: 'today', label: '今日' },
            { value: '7days', label: '過去7日間' },
            { value: '30days', label: '過去30日間' },
            { value: '90days', label: '過去90日間' },
          ]}
        />

        <Dropdown
          label="スコア"
          icon={<span>●</span>}
          value={value.score}
          onChange={(score) => onChange({ ...value, score: score as HistoryFilterState['score'] })}
          options={[
            { value: 'all', label: '全スコア' },
            { value: 'excellent', label: '優秀 (80-100)' },
            { value: 'good', label: '良好 (60-79)' },
            { value: 'warning', label: '要改善 (40-59)' },
            { value: 'danger', label: '危険 (0-39)' },
          ]}
        />

        <Dropdown
          label="観点"
          icon={<Layers className="w-3 h-3" />}
          value={value.aspect}
          onChange={(aspect) =>
            onChange({ ...value, aspect: aspect as HistoryFilterState['aspect'] })
          }
          options={[
            { value: 'all', label: '全観点' },
            { value: 'asvs', label: 'OWASP ASVS 網羅性' },
            { value: 'sast', label: '静的解析 (Semgrep)' },
            { value: 'dast', label: '動的スキャン (ZAP)' },
          ]}
        />

        {isFiltered ? (
          <button
            onClick={onClear}
            className="px-3 py-1.5 rounded-lg border transition hover:opacity-80 inline-flex items-center gap-1.5 text-xs"
            style={{ borderColor: 'var(--accent-blue)', color: 'var(--accent-blue)' }}
          >
            <X className="w-3 h-3" />
            クリア
          </button>
        ) : null}
      </div>
    </>
  );
}
