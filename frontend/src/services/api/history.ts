/**
 * History API
 */

import { apiClient } from './client';
import type { HistoryResponse } from '../../types/api';

export interface HistoryFilters {
  query?: string;
  period?: string;
  scoreRange?: string;
  perspective?: string;
}

export const historyApi = {
  /**
   * Get review history with optional filters
   */
  getHistory(filters?: HistoryFilters): Promise<HistoryResponse> {
    return apiClient.get<HistoryResponse>('/api/history', filters as Record<string, string | undefined>);
  },

  /**
   * List review history (alias for getHistory)
   */
  list(filters?: HistoryFilters): Promise<HistoryResponse> {
    return apiClient.get<HistoryResponse>('/api/history', filters as Record<string, string | undefined>);
  },
};
