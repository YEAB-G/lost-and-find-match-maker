/**
 * MatchCard component for displaying a single match result.
 *
 * Shows:
 * - Match strength badge
 * - Score percentage
 * - Matched report details
 * - Reasons for the match
 * - Expandable factor scores
 */

import { useState } from 'react';
import { type MatchDetail } from '../api';
import './MatchCard.css';

interface MatchCardProps {
  match: MatchDetail;
  rank: number;
  reportType: 'lost' | 'found';
}

export default function MatchCard({ match, rank, reportType }: MatchCardProps) {
  const [showFactors, setShowFactors] = useState(false);

  const { matched_report, score, strength, reasons, factor_scores } = match;

  const getStrengthColor = (strength: string) => {
    switch (strength) {
      case 'strong': return '#22c55e';
      case 'possible': return '#eab308';
      case 'weak': return '#f97316';
      default: return '#6b7280';
    }
  };

  const getStrengthLabel = (strength: string) => {
    switch (strength) {
      case 'strong': return 'Strong Match';
      case 'possible': return 'Possible Match';
      case 'weak': return 'Weak Match';
      default: return 'Match';
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className={`match-card ${strength}`}>
      {/* Header with Score */}
      <div className="match-header">
        <div className="rank">#{rank}</div>
        <div className="score-section">
          <div
            className="score-circle"
            style={{ borderColor: getStrengthColor(strength) }}
          >
            <span className="score-value">{Math.round(score)}</span>
            <span className="score-unit">%</span>
          </div>
          <span
            className="strength-badge"
            style={{ backgroundColor: getStrengthColor(strength) }}
          >
            {getStrengthLabel(strength)}
          </span>
        </div>
      </div>

      {/* Matched Report Info */}
      <div className="matched-report">
        <div className="report-type-label">
          {reportType === 'lost' ? '🟢 Found' : '🔴 Lost'}:
        </div>
        <h3 className="matched-title">{matched_report.title}</h3>
        <p className="matched-description">{matched_report.description}</p>
        <div className="matched-details">
          <span>📍 {matched_report.location}</span>
          {matched_report.category && (
            <span>📂 {matched_report.category.charAt(0).toUpperCase() + matched_report.category.slice(1)}</span>
          )}
          {matched_report.color && (
            <span>🎨 {matched_report.color.charAt(0).toUpperCase() + matched_report.color.slice(1)}</span>
          )}
          <span>📅 {formatDate(matched_report.reported_at)}</span>
        </div>
      </div>

      {/* Reasons */}
      {reasons.length > 0 && (
        <div className="reasons-section">
          <h4>Why this may match:</h4>
          <ul className="reasons-list">
            {reasons.map((reason, index) => (
              <li key={index} className="reason-item">
                <span className="reason-check">✓</span>
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Factor Scores (Expandable) */}
      <div className="factors-section">
        <button
          className="factors-toggle"
          onClick={() => setShowFactors(!showFactors)}
        >
          {showFactors ? 'Hide' : 'Show'} scoring details
          <span className="toggle-arrow">{showFactors ? '▲' : '▼'}</span>
        </button>

        {showFactors && (
          <div className="factors-grid">
            {Object.entries(factor_scores).map(([factor, value]) => (
              <div key={factor} className="factor-item">
                <span className="factor-name">
                  {factor.charAt(0).toUpperCase() + factor.slice(1)}
                </span>
                <span className="factor-value">
                  {value !== null ? `${Math.round(value)}` : 'N/A'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
