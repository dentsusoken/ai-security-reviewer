/**
 * Dashboard API
 */

import { apiClient } from './client';
import type { DashboardStats } from '../../types/api';

export const dashboardApi = {
  /**
   * Get dashboard statistics
   */
  getStats(): Promise<DashboardStats> {
    return apiClient.get<DashboardStats>('/api/dashboard/stats');
  },
};
