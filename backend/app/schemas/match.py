"""
Schemas for match-related API responses.
"""

from typing import Optional

from pydantic import BaseModel

from app.schemas.report import ReportResponse


class MatchDetail(BaseModel):
    """A single match result with the matched report."""

    matched_report: ReportResponse
    score: float
    strength: str
    reasons: list[str]
    factor_scores: dict[str, Optional[float]]


class MatchResponse(BaseModel):
    """Response for GET /reports/{report_id}/matches."""

    report: ReportResponse
    matches: list[MatchDetail]
    total_candidates: int
    qualifying_matches: int
