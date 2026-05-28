export type Theme = 'dark' | 'light';

export interface Review {
  id: string;
  repoName: string;
  branch: string;
  score: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  timestamp: string;
}

export interface Dashboard {
  totalReviews: number;
  totalFindings: number;
  fixedFindings: number;
  averageScore: number;
  recentReviews: Review[];
}
