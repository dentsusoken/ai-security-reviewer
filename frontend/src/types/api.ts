/**
 * API Response Types
 * Matches backend Pydantic schemas
 */

// Enums
export type InputType = 'github' | 'code' | 'url';
export type Perspective = 'asvs' | 'sast' | 'dast';
export type ReviewDepth = 'quick' | 'standard' | 'detailed';
export type Severity = 'critical' | 'high' | 'medium' | 'low';
export type ReviewStatus = 'queued' | 'running' | 'completed' | 'failed' | 'canceled';
export type ResolutionState = 'open' | 'resolved';
export type AgentName = 'SpecComplianceAgent' | 'SastAnalysisAgent' | 'ReportSynthesizerAgent';
export type AgentStatus = 'waiting' | 'running' | 'completed' | 'failed';

// Request types
export interface ReviewCreateRequest {
  inputType: InputType;
  repoUrl?: string;
  branch?: string;
  code?: string;
  filename?: string;
  language?: string;
  targetUrl?: string;
  perspectives: Perspective[];
  depth: ReviewDepth;
}

export interface FindingStatusUpdate {
  resolutionState: ResolutionState;
}

// Response types
export interface ReviewCreateResponse {
  reviewSessionId: string;
  status: ReviewStatus;
}

export interface ScoreSummary {
  overall: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface PerspectiveScore {
  category: string;
  percentage: number;
}

export interface ReviewDetail {
  id: string;
  status: ReviewStatus;
  inputType: InputType;
  repoUrl?: string;
  branch?: string;
  perspectives: Perspective[];
  depth: ReviewDepth;
  startedAt?: string;
  completedAt?: string;
  durationMs?: number;
  scoreSummary?: ScoreSummary;
  perspectiveScores?: PerspectiveScore[];
}

export interface HistoryReview {
  id: string;
  repoUrl: string;
  branch: string;
  inputType: InputType;
  perspectives: Perspective[];
  startedAt: string;
  durationMs: number;
  scoreSummary: ScoreSummary;
}

export interface HistoryResponse {
  reviews: HistoryReview[];
  totalCount: number;
}

export interface DashboardStats {
  totalReviews: number;
  totalFindings: number;
  resolvedFindings: number;
  averageScore: number;
  recentReviews: HistoryReview[];
}

// Finding types
export interface FindingSummary {
  id: string;
  severity: Severity;
  title: string;
  filePath: string;
  lineStart?: number;
  asvsRequirementIds: string[];
  cweIds: string[];
}

export interface FindingsResponse {
  findings: FindingSummary[];
}

export interface Reference {
  title: string;
  url: string;
}

export interface FindingDetail {
  id: string;
  reviewSessionId: string;
  severity: Severity;
  title: string;
  description: string;
  filePath: string;
  lineStart?: number;
  lineEnd?: number;
  detectedCode: string;
  fixSuggestion: string;
  aiExplanation: string;
  agentSource: string;
  asvsRequirementIds: string[];
  cweIds: string[];
  resolutionState: ResolutionState;
  references: Reference[];
}

// SSE Event types
export interface ProgressEvent {
  percent: number;
  message: string;
  elapsedMs: number;
  estimatedRemainingMs: number;
}

export interface AgentStateEvent {
  agentName: AgentName;
  status: AgentStatus;
  progressPercent?: number;
  currentActivity?: string;
  details?: string[];
}

export interface LogEvent {
  message: string;
  timestamp: string;
}

export interface CompletedEvent {
  reviewSessionId: string;
  status: ReviewStatus;
  message: string;
}

export type SSEEventType = 'progress' | 'agent_state' | 'log' | 'completed';
