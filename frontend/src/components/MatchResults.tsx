/**
 * MatchResults component for displaying potential matches for a report.
 *
 * Shows:
 * - The selected report details
 * - Ranked potential matches with scores and reasons
 * - Loading, error, and empty states
 */

import { useState, useEffect } from 'react';
import { fetchMatches, type MatchResponse } from '../api';
import MatchCard from './MatchCard';
import './MatchResults.css';

interface MatchResultsProps {
  reportId: number;
  onBack: () => void;
}

export default function MatchResults({ reportId, onBack }: MatchResultsProps) {
  const [data, setData] = useState<MatchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMatches();
  }, [reportId]);

  const loadMatches = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await fetchMatches(reportId);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load matches');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="match-results-container">
      {/* Back Button */}
      <button className="back-btn" onClick={onBack}>
        ← Back to Reports
      </button>

      {/* Loading State */}
      {isLoading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <span>Finding potential matches...</span>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="error-state">
          <div className="error-icon">❌</div>
          <h3>Unable to Load Matches</h3>
          <p>{error}</p>
          <button onClick={loadMatches} className="retry-btn">
            Try Again
          </button>
        </div>
      )}

      {/* Results */}
      {!isLoading && !error && data && (
        <>
          {/* Selected Report */}
          <div className="selected-report">
            <h2>Report Details</h2>
            <div className="report-info">
              <span className={`type-badge ${data.report.report_type}`}>
                {data.report.report_type === 'lost' ? '🔴 Lost' : '🟢 Found'}
              </span>
              <h3>{data.report.title}</h3>
              <p className="description">{data.report.description}</p>
              <div className="details">
                <span>📍 {data.report.location}</span>
                {data.report.category && (
                  <span>📂 {data.report.category.charAt(0).toUpperCase() + data.report.category.slice(1)}</span>
                )}
                {data.report.color && (
                  <span>🎨 {data.report.color.charAt(0).toUpperCase() + data.report.color.slice(1)}</span>
                )}
                <span>📅 {formatDate(data.report.reported_at)}</span>
              </div>
            </div>
          </div>

          {/* Match Summary */}
          <div className="match-summary">
            <h2>Potential Matches</h2>
            <p className="summary-text">
              {data.total_candidates === 0
                ? `No ${data.report.report_type === 'lost' ? 'found' : 'lost'} reports in the system yet.`
                : `Checked ${data.total_candidates} candidate${data.total_candidates !== 1 ? 's' : ''}.`}
              {' '}
              {data.qualifying_matches > 0
                ? `${data.qualifying_matches} potential match${data.qualifying_matches !== 1 ? 'es' : ''} found.`
                : 'No matches met the threshold.'}
            </p>
          </div>

          {/* No Matches */}
          {data.matches.length === 0 && (
            <div className="no-matches">
              <div className="no-matches-icon">🔍</div>
              <h3>No Strong Potential Matches Found</h3>
              <p>
                New reports may create a match later.
                {data.report.report_type === 'lost'
                  ? ' Keep checking back as new found items are reported.'
                  : ' Keep checking back as new lost items are reported.'}
              </p>
            </div>
          )}

          {/* Match Cards */}
          {data.matches.length > 0 && (
            <div className="matches-list">
              {data.matches.map((match, index) => (
                <MatchCard
                  key={match.matched_report.id}
                  match={match}
                  rank={index + 1}
                  reportType={data.report.report_type}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
