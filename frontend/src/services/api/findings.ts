/**
 * Findings API
 */

import { apiClient } from './client';
import type { FindingDetail, FindingStatusUpdate } from '../../types/api';

export const findingsApi = {
  /**
   * Get finding details by ID
   */
  getById(findingId: string): Promise<FindingDetail> {
    return apiClient.get<FindingDetail>(`/api/findings/${findingId}`);
  },

  /**
   * Update finding resolution status
   */
  updateStatus(findingId: string, data: FindingStatusUpdate): Promise<FindingDetail> {
    return apiClient.patch<FindingDetail>(`/api/findings/${findingId}/status`, data);
  },
};
