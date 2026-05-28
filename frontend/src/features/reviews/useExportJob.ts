/**
 * Export job hook for status polling and download management.
 *
 * Handles async export job creation, progress tracking, and file downloads.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { exportsApi } from '../../services/api';

/**
 * Export format type.
 */
export type ExportFormat = 'excel' | 'markdown' | 'pdf' | 'json';

/**
 * Export section options.
 */
export interface ExportSections {
  /** Include summary section */
  summary: boolean;
  /** Include perspective scores */
  perspectives: boolean;
  /** Include all findings */
  findings: boolean;
  /** Include code fix suggestions */
  codeFixes: boolean;
}

/**
 * Export job status.
 */
export type ExportJobStatus = 'idle' | 'creating' | 'processing' | 'completed' | 'failed';

/**
 * Export job state.
 */
export interface ExportJobState {
  /** Current job status */
  status: ExportJobStatus;
  /** Job ID (set after creation) */
  jobId: string | null;
  /** Progress percentage (0-100) */
  progress: number;
  /** Error message if failed */
  error: string | null;
  /** Download URL when completed */
  downloadUrl: string | null;
}

/**
 * Export job hook result.
 */
export interface UseExportJobResult {
  /** Current job state */
  state: ExportJobState;
  /** Start a new export job */
  startExport: (options: {
    reviewId: string;
    format: ExportFormat;
    sections: ExportSections;
  }) => Promise<void>;
  /** Download the completed export */
  download: () => Promise<void>;
  /** Reset the job state */
  reset: () => void;
  /** Whether an export is in progress */
  isExporting: boolean;
  /** Whether download is ready */
  isReady: boolean;
}

const INITIAL_STATE: ExportJobState = {
  status: 'idle',
  jobId: null,
  progress: 0,
  error: null,
  downloadUrl: null,
};

/** Polling interval in milliseconds */
const POLL_INTERVAL = 2000;

/** Maximum polling attempts */
const MAX_POLL_ATTEMPTS = 60;

/**
 * Hook for managing export jobs with status polling.
 *
 * @param options - Hook options
 * @returns Export job state and actions
 *
 * @example
 * ```tsx
 * const { state, startExport, download, isExporting, isReady } = useExportJob();
 *
 * // Start export
 * await startExport({
 *   reviewId: 'review-123',
 *   format: 'excel',
 *   sections: { summary: true, perspectives: true, findings: true, codeFixes: true },
 * });
 *
 * // Download when ready
 * if (isReady) {
 *   await download();
 * }
 * ```
 */
export function useExportJob(): UseExportJobResult {
  const [state, setState] = useState<ExportJobState>(INITIAL_STATE);
  const pollCountRef = useRef(0);
  const pollTimerRef = useRef<number | null>(null);

  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (pollTimerRef.current) {
        clearTimeout(pollTimerRef.current);
      }
    };
  }, []);

  /**
   * Poll for job status.
   */
  const pollStatus = useCallback(async (jobId: string) => {
    try {
      const response = await exportsApi.getJobStatus(jobId);

      if (response.status === 'completed') {
        setState((prev) => ({
          ...prev,
          status: 'completed',
          progress: 100,
          downloadUrl: response.downloadUrl,
        }));
        return;
      }

      if (response.status === 'failed') {
        setState((prev) => ({
          ...prev,
          status: 'failed',
          error: response.error || 'エクスポートに失敗しました',
        }));
        return;
      }

      // Update progress
      setState((prev) => ({
        ...prev,
        progress: response.progress || prev.progress,
      }));

      // Continue polling
      pollCountRef.current += 1;
      if (pollCountRef.current < MAX_POLL_ATTEMPTS) {
        pollTimerRef.current = window.setTimeout(() => {
          pollStatus(jobId);
        }, POLL_INTERVAL);
      } else {
        setState((prev) => ({
          ...prev,
          status: 'failed',
          error: 'タイムアウト: エクスポート処理に時間がかかりすぎています',
        }));
      }
    } catch (err) {
      console.error('Failed to poll export status:', err);
      setState((prev) => ({
        ...prev,
        status: 'failed',
        error: 'ステータスの取得に失敗しました',
      }));
    }
  }, []);

  /**
   * Start a new export job.
   */
  const startExport = useCallback(
    async (options: { reviewId: string; format: ExportFormat; sections: ExportSections }) => {
      // Reset state
      pollCountRef.current = 0;
      if (pollTimerRef.current) {
        clearTimeout(pollTimerRef.current);
      }

      setState({
        ...INITIAL_STATE,
        status: 'creating',
      });

      try {
        // For Excel, use direct download (sync)
        if (options.format === 'excel') {
          setState((prev) => ({ ...prev, status: 'processing', progress: 50 }));
          await exportsApi.downloadExcel(options.reviewId);
          setState({
            ...INITIAL_STATE,
            status: 'completed',
            progress: 100,
          });
          return;
        }

        // For other formats, create async job
        const response = await exportsApi.createJob({
          reviewId: options.reviewId,
          format: options.format,
          sections: Object.entries(options.sections)
            .filter(([, enabled]) => enabled)
            .map(([key]) => key),
        });

        setState((prev) => ({
          ...prev,
          status: 'processing',
          jobId: response.jobId,
          progress: 10,
        }));

        // Start polling
        pollStatus(response.jobId);
      } catch (err) {
        console.error('Failed to start export:', err);
        setState((prev) => ({
          ...prev,
          status: 'failed',
          error: 'エクスポートの開始に失敗しました',
        }));
      }
    },
    [pollStatus]
  );

  /**
   * Download the completed export.
   */
  const download = useCallback(async () => {
    if (!state.downloadUrl) {
      console.error('No download URL available');
      return;
    }

    try {
      // Trigger browser download
      const link = document.createElement('a');
      link.href = state.downloadUrl;
      link.download = '';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Failed to download:', err);
      setState((prev) => ({
        ...prev,
        error: 'ダウンロードに失敗しました',
      }));
    }
  }, [state.downloadUrl]);

  /**
   * Reset job state.
   */
  const reset = useCallback(() => {
    if (pollTimerRef.current) {
      clearTimeout(pollTimerRef.current);
    }
    pollCountRef.current = 0;
    setState(INITIAL_STATE);
  }, []);

  return {
    state,
    startExport,
    download,
    reset,
    isExporting: state.status === 'creating' || state.status === 'processing',
    isReady: state.status === 'completed' && !!state.downloadUrl,
  };
}

/**
 * Default export sections.
 */
export const DEFAULT_EXPORT_SECTIONS: ExportSections = {
  summary: true,
  perspectives: true,
  findings: true,
  codeFixes: true,
};

/**
 * Format display info.
 */
export const FORMAT_INFO: Record<
  ExportFormat,
  { label: string; extension: string; available: boolean }
> = {
  excel: { label: 'Excel', extension: '.xlsx', available: true },
  markdown: { label: 'Markdown', extension: '.md', available: false },
  pdf: { label: 'PDF', extension: '.pdf', available: false },
  json: { label: 'JSON', extension: '.json', available: false },
};
