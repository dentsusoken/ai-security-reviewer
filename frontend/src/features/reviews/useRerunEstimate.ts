/**
 * Re-review time estimate calculation hook.
 *
 * Provides dynamic time estimates based on review options.
 */
import { useMemo } from 'react';

/**
 * Review options that affect time estimate.
 */
export interface ReviewOptions {
  /** Analysis depth (quick, standard, deep) */
  depth: 'quick' | 'standard' | 'deep';
  /** Selected perspectives */
  perspectives: string[];
  /** Target repository size (optional, in KB) */
  repoSize?: number;
  /** Number of files (optional) */
  fileCount?: number;
}

/**
 * Time estimate result.
 */
export interface TimeEstimate {
  /** Minimum time in minutes */
  minMinutes: number;
  /** Maximum time in minutes */
  maxMinutes: number;
  /** Formatted display string */
  display: string;
  /** Display string in Japanese */
  displayJa: string;
}

/**
 * Base time estimates per depth in minutes.
 */
const DEPTH_BASE_TIME: Record<string, { min: number; max: number }> = {
  quick: { min: 1, max: 3 },
  standard: { min: 3, max: 7 },
  deep: { min: 8, max: 15 },
};

/**
 * Additional time per perspective in minutes.
 */
const PERSPECTIVE_TIME: Record<string, number> = {
  asvs: 2,
  sast: 3,
  dast: 5,
  secrets: 1,
  dependencies: 2,
};

/**
 * Calculate time multiplier based on repo size.
 */
function calculateSizeMultiplier(sizeKb?: number): number {
  if (!sizeKb) return 1;

  // Small repos (< 1MB): 1x
  if (sizeKb < 1024) return 1;
  // Medium repos (1-10MB): 1.5x
  if (sizeKb < 10240) return 1.5;
  // Large repos (10-50MB): 2x
  if (sizeKb < 51200) return 2;
  // Very large repos (> 50MB): 2.5x
  return 2.5;
}

/**
 * Calculate time multiplier based on file count.
 */
function calculateFileMultiplier(fileCount?: number): number {
  if (!fileCount) return 1;

  // Small projects (< 50 files): 1x
  if (fileCount < 50) return 1;
  // Medium projects (50-200 files): 1.3x
  if (fileCount < 200) return 1.3;
  // Large projects (200-500 files): 1.6x
  if (fileCount < 500) return 1.6;
  // Very large projects (> 500 files): 2x
  return 2;
}

/**
 * Format time range for display.
 */
function formatTimeRange(minMinutes: number, maxMinutes: number): string {
  // Round to nearest minute
  const min = Math.round(minMinutes);
  const max = Math.round(maxMinutes);

  if (min === max) {
    return `~${min} min`;
  }
  return `${min}-${max} min`;
}

/**
 * Format time range for Japanese display.
 */
function formatTimeRangeJa(minMinutes: number, maxMinutes: number): string {
  const min = Math.round(minMinutes);
  const max = Math.round(maxMinutes);

  if (min === max) {
    return `約${min}分`;
  }
  return `${min}〜${max}分`;
}

/**
 * Hook for calculating dynamic review time estimates.
 *
 * @param options - Review options affecting time
 * @returns Time estimate with min/max and formatted display
 *
 * @example
 * ```tsx
 * const { display, displayJa, minMinutes } = useRerunEstimate({
 *   depth: 'standard',
 *   perspectives: ['asvs', 'sast'],
 *   repoSize: 5120, // 5MB
 * });
 *
 * return <span>予想時間: {displayJa}</span>;
 * ```
 */
export function useRerunEstimate(options: ReviewOptions): TimeEstimate {
  return useMemo(() => {
    const { depth, perspectives, repoSize, fileCount } = options;

    // Get base time for depth
    const baseTime = DEPTH_BASE_TIME[depth] || DEPTH_BASE_TIME.standard;

    // Calculate perspective time
    let perspectiveTime = 0;
    for (const perspective of perspectives) {
      perspectiveTime += PERSPECTIVE_TIME[perspective] || 1;
    }

    // Apply multipliers
    const sizeMultiplier = calculateSizeMultiplier(repoSize);
    const fileMultiplier = calculateFileMultiplier(fileCount);
    const combinedMultiplier = Math.max(sizeMultiplier, fileMultiplier);

    // Calculate final estimates
    const minMinutes = (baseTime.min + perspectiveTime * 0.5) * combinedMultiplier;
    const maxMinutes = (baseTime.max + perspectiveTime) * combinedMultiplier;

    return {
      minMinutes,
      maxMinutes,
      display: formatTimeRange(minMinutes, maxMinutes),
      displayJa: formatTimeRangeJa(minMinutes, maxMinutes),
    };
  }, [options]);
}

/**
 * Get estimate for quick preview (without full calculation).
 */
export function getQuickEstimate(
  depth: 'quick' | 'standard' | 'deep',
  perspectiveCount: number
): string {
  const base = DEPTH_BASE_TIME[depth] || DEPTH_BASE_TIME.standard;
  const additional = perspectiveCount * 1.5;
  const min = Math.round(base.min + additional * 0.5);
  const max = Math.round(base.max + additional);
  return `${min}〜${max}分`;
}

/**
 * Available depth options with labels.
 */
export const DEPTH_OPTIONS = [
  {
    value: 'quick',
    label: 'クイック',
    labelEn: 'Quick',
    description: '主要ファイルのみを対象とした高速スキャン',
    descriptionEn: 'Fast scan of key files only',
  },
  {
    value: 'standard',
    label: '標準',
    labelEn: 'Standard',
    description: '全ファイルを対象とした標準的な分析',
    descriptionEn: 'Standard analysis of all files',
  },
  {
    value: 'deep',
    label: 'ディープ',
    labelEn: 'Deep',
    description: '詳細なコンテキスト分析を含む徹底的なレビュー',
    descriptionEn: 'Thorough review with detailed context analysis',
  },
] as const;

/**
 * Available perspective options with labels.
 */
export const PERSPECTIVE_OPTIONS = [
  {
    value: 'asvs',
    label: 'ASVS準拠',
    labelEn: 'ASVS Compliance',
    description: 'OWASP ASVS標準に基づく検証',
  },
  {
    value: 'sast',
    label: 'SAST分析',
    labelEn: 'SAST Analysis',
    description: '静的アプリケーションセキュリティテスト',
  },
  {
    value: 'dast',
    label: 'DAST分析',
    labelEn: 'DAST Analysis',
    description: '動的アプリケーションセキュリティテスト',
  },
  {
    value: 'secrets',
    label: 'シークレット検出',
    labelEn: 'Secret Detection',
    description: 'ハードコードされた認証情報の検出',
  },
  {
    value: 'dependencies',
    label: '依存関係分析',
    labelEn: 'Dependency Analysis',
    description: 'サードパーティライブラリの脆弱性チェック',
  },
] as const;
