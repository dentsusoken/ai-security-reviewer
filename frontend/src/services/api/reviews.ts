/**
 * Reviews API
 */

import { apiClient } from './client';
import type {
  ReviewCreateRequest,
  ReviewCreateResponse,
  ReviewDetail,
  FindingsResponse,
} from '../../types/api';

export const reviewsApi = {
  /**
   * Create a new review session
   */
  create(data: ReviewCreateRequest): Promise<ReviewCreateResponse> {
    return apiClient.post<ReviewCreateResponse>('/api/reviews', data);
  },

  /**
   * Get review details by ID
   */
  getById(reviewSessionId: string): Promise<ReviewDetail> {
    return apiClient.get<ReviewDetail>(`/api/reviews/${reviewSessionId}`);
  },

  /**
   * Get findings for a review
   */
  getFindings(reviewSessionId: string): Promise<FindingsResponse> {
    return apiClient.get<FindingsResponse>(`/api/reviews/${reviewSessionId}/findings`);
  },
};
