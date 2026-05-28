/**
 * Evidence Panel component for displaying ASVS and CWE references.
 *
 * Shows security standard compliance mappings with links to official documentation.
 */
import { BookOpen, ExternalLink, Shield, AlertTriangle } from 'lucide-react';

/**
 * ASVS requirement reference.
 */
export interface ASVSRequirement {
  /** Requirement ID (e.g., "V2.1.1") */
  id: string;
  /** Category name */
  category?: string;
  /** Description */
  description?: string;
  /** Level (1, 2, or 3) */
  level?: number;
}

/**
 * CWE reference.
 */
export interface CWEReference {
  /** CWE ID (number) */
  id: number;
  /** CWE name */
  name?: string;
  /** Brief description */
  description?: string;
}

interface EvidencePanelProps {
  /** ASVS requirement IDs */
  asvsRequirementIds?: string[];
  /** CWE IDs */
  cweIds?: number[];
  /** Additional references */
  references?: Array<{
    title: string;
    url: string;
  }>;
  /** Whether to show compact view */
  compact?: boolean;
}

/**
 * ASVS category mapping.
 */
const ASVS_CATEGORIES: Record<string, string> = {
  'V1': 'アーキテクチャ、設計、脅威モデリング',
  'V2': '認証',
  'V3': 'セッション管理',
  'V4': 'アクセス制御',
  'V5': '検証、サニタイズ、エンコーディング',
  'V6': '保存時の暗号化',
  'V7': 'エラー処理とロギング',
  'V8': 'データ保護',
  'V9': '通信',
  'V10': '悪意のあるコード',
  'V11': 'ビジネスロジック',
  'V12': 'ファイルとリソース',
  'V13': 'API と Web サービス',
  'V14': '構成',
};

/**
 * Common CWE descriptions.
 */
const CWE_NAMES: Record<number, string> = {
  79: 'クロスサイトスクリプティング (XSS)',
  89: 'SQL インジェクション',
  94: 'コード インジェクション',
  200: '情報漏洩',
  269: '不適切な権限管理',
  284: 'アクセス制御の不備',
  287: '認証の不備',
  295: '証明書検証の不備',
  311: '機密データの暗号化の欠如',
  327: '脆弱な暗号アルゴリズム',
  352: 'クロスサイトリクエストフォージェリ (CSRF)',
  434: '危険なファイルタイプのアップロード',
  502: '安全でないデシリアライゼーション',
  522: '資格情報の不十分な保護',
  601: 'オープンリダイレクト',
  611: 'XML 外部エンティティ (XXE)',
  798: 'ハードコードされた認証情報',
  918: 'サーバーサイドリクエストフォージェリ (SSRF)',
};

/**
 * Get ASVS category from requirement ID.
 */
function getASVSCategory(id: string): string {
  const match = id.match(/^V(\d+)/);
  if (match) {
    const category = `V${match[1]}`;
    return ASVS_CATEGORIES[category] || category;
  }
  return '不明なカテゴリ';
}

/**
 * Get CWE name from ID.
 */
function getCWEName(id: number): string {
  return CWE_NAMES[id] || `CWE-${id}`;
}

/**
 * Evidence Panel component for displaying security standard references.
 */
export function EvidencePanel({
  asvsRequirementIds = [],
  cweIds = [],
  references = [],
  compact = false,
}: EvidencePanelProps) {
  const hasASVS = asvsRequirementIds.length > 0;
  const hasCWE = cweIds.length > 0;
  const hasReferences = references.length > 0;

  if (!hasASVS && !hasCWE && !hasReferences) {
    return null;
  }

  if (compact) {
    return (
      <div className="flex flex-wrap gap-2">
        {asvsRequirementIds.map((id) => (
          <a
            key={id}
            href={`https://owasp.org/www-project-application-security-verification-standard/`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-mono transition hover:opacity-80"
            style={{
              background: 'rgba(79, 139, 255, 0.15)',
              color: 'var(--accent-blue)',
              border: '1px solid rgba(79, 139, 255, 0.3)',
            }}
          >
            <Shield className="w-3 h-3" />
            {id}
          </a>
        ))}
        {cweIds.map((id) => (
          <a
            key={id}
            href={`https://cwe.mitre.org/data/definitions/${id}.html`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-mono transition hover:opacity-80"
            style={{
              background: 'rgba(234, 88, 12, 0.15)',
              color: '#EA580C',
              border: '1px solid rgba(234, 88, 12, 0.3)',
            }}
          >
            <AlertTriangle className="w-3 h-3" />
            CWE-{id}
          </a>
        ))}
      </div>
    );
  }

  return (
    <div className="glass rounded-xl overflow-hidden">
      <div
        className="px-4 py-3 border-b flex items-center gap-2"
        style={{ borderColor: 'var(--border)', background: 'var(--bg-elevated)' }}
      >
        <BookOpen className="w-4 h-4" style={{ color: 'var(--accent-cyan)' }} />
        <span className="font-semibold text-sm">セキュリティ基準への準拠</span>
      </div>

      <div className="p-4 space-y-4">
        {/* ASVS Requirements */}
        {hasASVS && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-4 h-4" style={{ color: 'var(--accent-blue)' }} />
              <span className="text-sm font-medium">OWASP ASVS 要件</span>
            </div>
            <div className="space-y-2">
              {asvsRequirementIds.map((id) => (
                <a
                  key={id}
                  href={`https://owasp.org/www-project-application-security-verification-standard/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-3 rounded-lg transition hover:opacity-80"
                  style={{
                    background: 'rgba(79, 139, 255, 0.08)',
                    border: '1px solid rgba(79, 139, 255, 0.2)',
                  }}
                >
                  <div>
                    <div className="font-mono text-sm" style={{ color: 'var(--accent-blue)' }}>
                      {id}
                    </div>
                    <div className="text-xs mt-0.5" style={{ color: 'var(--text-tertiary)' }}>
                      {getASVSCategory(id)}
                    </div>
                  </div>
                  <ExternalLink className="w-4 h-4" style={{ color: 'var(--text-tertiary)' }} />
                </a>
              ))}
            </div>
          </div>
        )}

        {/* CWE References */}
        {hasCWE && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4" style={{ color: '#EA580C' }} />
              <span className="text-sm font-medium">CWE (共通脆弱性タイプ)</span>
            </div>
            <div className="space-y-2">
              {cweIds.map((id) => (
                <a
                  key={id}
                  href={`https://cwe.mitre.org/data/definitions/${id}.html`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-3 rounded-lg transition hover:opacity-80"
                  style={{
                    background: 'rgba(234, 88, 12, 0.08)',
                    border: '1px solid rgba(234, 88, 12, 0.2)',
                  }}
                >
                  <div>
                    <div className="font-mono text-sm" style={{ color: '#EA580C' }}>
                      CWE-{id}
                    </div>
                    <div className="text-xs mt-0.5" style={{ color: 'var(--text-tertiary)' }}>
                      {getCWEName(id)}
                    </div>
                  </div>
                  <ExternalLink className="w-4 h-4" style={{ color: 'var(--text-tertiary)' }} />
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Additional References */}
        {hasReferences && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <ExternalLink className="w-4 h-4" style={{ color: 'var(--text-secondary)' }} />
              <span className="text-sm font-medium">参考リンク</span>
            </div>
            <ul className="space-y-2">
              {references.map((ref, idx) => (
                <li key={idx}>
                  <a
                    href={ref.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm hover:underline"
                    style={{ color: 'var(--accent-blue)' }}
                  >
                    {ref.title}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
