"""
Matches API endpoint.

Provides GET /reports/{report_id}/matches to find potential matches
for a given report using the matching engine.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.schemas.match import MatchDetail, MatchResponse
from app.schemas.report import ReportResponse
from app.services.matcher import Report as MatcherReport, match_reports

router = APIRouter()

# Threshold for filtering out weak matches
MATCH_THRESHOLD = 40


def sqlalchemy_to_matcher_report(report: Report) -> MatcherReport:
    """Convert a SQLAlchemy Report to a matcher Report."""
    return MatcherReport(
        id=report.id,
        report_type=report.report_type,
        title=report.title,
        description=report.description,
        category=report.category,
        color=report.color,
        location=report.location,
        reported_at=report.reported_at,
        created_at=report.created_at,
    )


@router.get("/reports/{report_id}/matches", response_model=MatchResponse)
def get_matches(report_id: int, db: Session = Depends(get_db)):
    """
    Find potential matches for a given report.

    1. Find the selected report (404 if not found)
    2. Find reports with opposite type
    3. Compare each using the matching engine
    4. Filter out matches below threshold
    5. Sort by score (highest first)
    6. Return ranked matches with reasons
    """
    # Step 1: Find the selected report
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Step 2: Find reports with opposite type
    opposite_type = "found" if report.report_type == "lost" else "lost"
    candidates = (
        db.query(Report)
        .filter(Report.report_type == opposite_type)
        .all()
    )

    # Step 3: Compare each candidate using the matching engine
    matcher_report = sqlalchemy_to_matcher_report(report)
    all_matches = []

    for candidate in candidates:
        candidate_matcher = sqlalchemy_to_matcher_report(candidate)
        result = match_reports(matcher_report, candidate_matcher)

        if result is not None:
            all_matches.append(
                MatchDetail(
                    matched_report=ReportResponse.model_validate(candidate),
                    score=result.score,
                    strength=result.strength,
                    reasons=result.reasons,
                    factor_scores=result.factor_scores,
                )
            )

    # Step 4: Filter out matches below threshold
    qualifying_matches = [
        m for m in all_matches if m.score >= MATCH_THRESHOLD
    ]

    # Step 5: Sort by score (highest first)
    qualifying_matches.sort(key=lambda m: m.score, reverse=True)

    # Step 6: Return response
    return MatchResponse(
        report=ReportResponse.model_validate(report),
        matches=qualifying_matches,
        total_candidates=len(candidates),
        qualifying_matches=len(qualifying_matches),
    )
