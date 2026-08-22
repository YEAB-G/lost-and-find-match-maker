/**
 * API service for University Lost & Found Matcher.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ============================================================================
// Types
// ============================================================================

export interface Report {
  id: number;
  report_type: 'lost' | 'found';
  title: string;
  description: string;
  category: string | null;
  color: string | null;
  location: string;
  reported_at: string;
  created_at: string;
}

export interface ReportCreate {
  report_type: 'lost' | 'found';
  title: string;
  description: string;
  category?: string | null;
  color?: string | null;
  location: string;
  reported_at: string;
}

export interface ReportListResponse {
  reports: Report[];
  count: number;
}

export interface MatchDetail {
  matched_report: Report;
  score: number;
  strength: 'strong' | 'possible' | 'weak' | 'below_threshold';
  reasons: string[];
  factor_scores: Record<string, number | null>;
}

export interface MatchResponse {
  report: Report;
  matches: MatchDetail[];
  total_candidates: number;
  qualifying_matches: number;
}

// ============================================================================
// API Functions
// ============================================================================

export async function fetchReports(type?: string): Promise<ReportListResponse> {
  const url = type
    ? `${API_BASE}/reports?type=${type}`
    : `${API_BASE}/reports`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch reports: ${response.statusText}`);
  }
  return response.json();
}

export async function createReport(report: ReportCreate): Promise<Report> {
  const response = await fetch(`${API_BASE}/reports`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(report),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create report');
  }

  return response.json();
}

export async function fetchMatches(reportId: number): Promise<MatchResponse> {
  const response = await fetch(`${API_BASE}/reports/${reportId}/matches`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch matches');
  }
  return response.json();
}

// ============================================================================
// Constants
// ============================================================================

export const CATEGORIES = [
  'electronics',
  'bags',
  'clothing',
  'keys',
  'documents',
  'accessories',
  'other',
];

export const COLORS = [
  'black',
  'white',
  'blue',
  'red',
  'green',
  'grey',
  'brown',
  'pink',
  'purple',
  'yellow',
  'orange',
  'silver',
  'gold',
  'navy',
  'maroon',
  'dark',
  'light',
  'multicolor',
];
