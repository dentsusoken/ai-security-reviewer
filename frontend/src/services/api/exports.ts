/**
 * Exports API - File export operations
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Export job creation request.
 */
export interface CreateJobRequest {
  reviewId: string;
  format: string;
  sections: string[];
}

/**
 * Export job creation response.
 */
export interface CreateJobResponse {
  jobId: string;
  status: string;
}

/**
 * Export job status response.
 */
export interface JobStatusResponse {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  downloadUrl?: string;
  error?: string;
}

/**
 * Download review results as Excel file
 */
export async function downloadExcel(reviewId: string): Promise<void> {
  const url = `${API_BASE_URL}/api/reviews/${reviewId}/export/excel`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    },
  });

  if (!response.ok) {
    throw new Error(`Export failed: ${response.status} ${response.statusText}`);
  }

  // Get filename from Content-Disposition header
  const contentDisposition = response.headers.get('Content-Disposition');
  let filename = `security-review-${reviewId}.xlsx`;

  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="?([^";\n]+)"?/);
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1];
    }
  }

  // Convert response to blob
  const blob = await response.blob();

  // Create download link
  const downloadUrl = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = filename;

  // Trigger download
  document.body.appendChild(link);
  link.click();

  // Cleanup
  document.body.removeChild(link);
  URL.revokeObjectURL(downloadUrl);
}

/**
 * Create an async export job for non-Excel formats.
 */
export async function createJob(request: CreateJobRequest): Promise<CreateJobResponse> {
  const url = `${API_BASE_URL}/api/exports`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Create job failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get the status of an export job.
 */
export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const url = `${API_BASE_URL}/api/exports/${jobId}`;

  const response = await fetch(url, {
    method: 'GET',
  });

  if (!response.ok) {
    throw new Error(`Get job status failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export const exportsApi = {
  downloadExcel,
  createJob,
  getJobStatus,
};
