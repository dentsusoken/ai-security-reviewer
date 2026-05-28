/**
 * SSE Events API for real-time progress streaming
 */

import { API_BASE_URL } from './client';
import type {
  AgentStatus,
} from '../../types/api';

// Backend event data types (actual format from backend)
export interface BackendProgressEvent {
  percent: number;
  message: string;
}

export interface BackendAgentProgressEvent {
  agent_name: string;
  status: AgentStatus;
  progress_percent?: number;
  message?: string;
}

export interface BackendFetchingEvent {
  message: string;
  file_count?: number;
  current?: number;
  total?: number;
}

export interface BackendCompletedEvent {
  review_id: string;
  overall_score: number;
  findings_count: number;
}

export interface BackendErrorEvent {
  message: string;
}

export interface SSECallbacks {
  onProgress?: (data: BackendProgressEvent) => void;
  onAgentProgress?: (data: BackendAgentProgressEvent) => void;
  onFetching?: (eventType: string, data: BackendFetchingEvent) => void;
  onCompleted?: (data: BackendCompletedEvent) => void;
  onError?: (error: BackendErrorEvent) => void;
  onLog?: (message: string) => void;
}

/**
 * Connect to SSE stream for review progress
 * Returns a function to close the connection
 */
export function connectReviewEvents(
  reviewSessionId: string,
  callbacks: SSECallbacks
): () => void {
  const url = `${API_BASE_URL}/api/reviews/${reviewSessionId}/events`;
  const eventSource = new EventSource(url);

  // Progress event
  eventSource.addEventListener('progress', (event) => {
    try {
      const data = JSON.parse(event.data) as BackendProgressEvent;
      callbacks.onProgress?.(data);
      if (data.message) {
        callbacks.onLog?.(data.message);
      }
    } catch (error) {
      console.error('Failed to parse progress event:', error);
    }
  });

  // Agent progress event
  eventSource.addEventListener('agent_progress', (event) => {
    try {
      const data = JSON.parse(event.data) as BackendAgentProgressEvent;
      callbacks.onAgentProgress?.(data);
      if (data.message) {
        callbacks.onLog?.(`[${data.agent_name}] ${data.message}`);
      }
    } catch (error) {
      console.error('Failed to parse agent_progress event:', error);
    }
  });

  // Fetching events (fetching_repo, fetching_tree, files_found, fetching_file, files_fetched, analyzing_code)
  const fetchingEventTypes = [
    'fetching_repo',
    'fetching_tree',
    'files_found',
    'fetching_file',
    'files_fetched',
    'analyzing_code',
  ];

  fetchingEventTypes.forEach(eventType => {
    eventSource.addEventListener(eventType, (event) => {
      try {
        const data = JSON.parse(event.data) as BackendFetchingEvent;
        callbacks.onFetching?.(eventType, data);
        if (data.message) {
          callbacks.onLog?.(data.message);
        }
      } catch (error) {
        console.error(`Failed to parse ${eventType} event:`, error);
      }
    });
  });

  // Completed event
  eventSource.addEventListener('completed', (event) => {
    try {
      const data = JSON.parse(event.data) as BackendCompletedEvent;
      callbacks.onCompleted?.(data);
      callbacks.onLog?.(`✅ レビュー完了: スコア ${data.overall_score}, ${data.findings_count} 件の指摘`);
      eventSource.close();
    } catch (error) {
      console.error('Failed to parse completed event:', error);
    }
  });

  // Error event
  eventSource.addEventListener('error', (event) => {
    // Check if it's an SSE error event (with data) or connection error
    if (event instanceof MessageEvent && event.data) {
      try {
        const data = JSON.parse(event.data) as BackendErrorEvent;
        callbacks.onError?.(data);
        callbacks.onLog?.(`❌ エラー: ${data.message}`);
      } catch {
        // Parse error
      }
    } else {
      // Connection error
      console.error('SSE connection error:', event);
      callbacks.onError?.({ message: 'SSE connection failed' });
    }
    eventSource.close();
  });

  // Keepalive (ignore)
  eventSource.addEventListener('keepalive', () => {
    // Ignore keepalive events
  });

  // Return cleanup function
  return () => {
    eventSource.close();
  };
}
