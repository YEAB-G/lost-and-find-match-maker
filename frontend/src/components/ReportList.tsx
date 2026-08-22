/**
 * ReportList component for displaying lost and found reports.
 *
 * Supports:
 * - Filtering by type (all, lost, found)
 * - Displaying report details
 * - Loading and empty states
 */

import { useState, useEffect } from 'react';
import { fetchReports, type Report } from '../api';
import './ReportList.css';

interface ReportListProps {
  refreshTrigger: number;
  onViewMatches: (reportId: number) => void;
}

type FilterType = 'all' | 'lost' | 'found';

export default function ReportList({ refreshTrigger, onViewMatches }: ReportListProps) {
  const [reports, setReports] = useState<Report[]>([]);
  const [filter, setFilter] = useState<FilterType>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadReports();
  }, [refreshTrigger, filter]);

  const loadReports = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const typeParam = filter === 'all' ? undefined : filter;
      const data = await fetchReports(typeParam);
      setReports(data.reports);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reports');
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
    <div className="report-list-container">
      <div className="list-header">
        <h2>Reports</h2>
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            className={`filter-btn lost ${filter === 'lost' ? 'active' : ''}`}
            onClick={() => setFilter('lost')}
          >
            🔴 Lost
          </button>
          <button
            className={`filter-btn found ${filter === 'found' ? 'active' : ''}`}
            onClick={() => setFilter('found')}
          >
            🟢 Found
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <span>Loading reports...</span>
        </div>
      )}

      {error && (
        <div className="error-state">
          ❌ {error}
          <button onClick={loadReports} className="retry-btn">
            Retry
          </button>
        </div>
      )}

      {!isLoading && !error && reports.length === 0 && (
        <div className="empty-state">
          <p>📝 No reports yet.</p>
          <p>Create a report above to get started!</p>
        </div>
      )}

      {!isLoading && !error && reports.length > 0 && (
        <div className="reports-grid">
          {reports.map((report) => (
            <div
              key={report.id}
              className={`report-card ${report.report_type}`}
            >
              <div className="card-header">
                <span className={`type-badge ${report.report_type}`}>
                  {report.report_type === 'lost' ? '🔴 Lost' : '🟢 Found'}
                </span>
                <span className="report-id">#{report.id}</span>
              </div>

              <h3 className="card-title">{report.title}</h3>
              <p className="card-description">{report.description}</p>

              <div className="card-details">
                <div className="detail-row">
                  <span className="detail-label">📍 Location:</span>
                  <span className="detail-value">{report.location}</span>
                </div>
                {report.category && (
                  <div className="detail-row">
                    <span className="detail-label">📂 Category:</span>
                    <span className="detail-value">
                      {report.category.charAt(0).toUpperCase() + report.category.slice(1)}
                    </span>
                  </div>
                )}
                {report.color && (
                  <div className="detail-row">
                    <span className="detail-label">🎨 Color:</span>
                    <span className="detail-value">
                      {report.color.charAt(0).toUpperCase() + report.color.slice(1)}
                    </span>
                  </div>
                )}
                <div className="detail-row">
                  <span className="detail-label">📅 Reported:</span>
                  <span className="detail-value">{formatDate(report.reported_at)}</span>
                </div>
              </div>

              <button
                className="matches-btn"
                onClick={() => onViewMatches(report.id)}
              >
                🔍 Find Matches
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
