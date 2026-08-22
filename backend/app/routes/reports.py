from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.schemas.report import (
    ReportCreate,
    ReportListResponse,
    ReportResponse,
)

router = APIRouter()


@router.post("/reports", response_model=ReportResponse, status_code=201)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    """Create a new lost or found report."""
    # Check for future reported_at
    now = datetime.now(timezone.utc)
    reported_at = report.reported_at.replace(tzinfo=None)
    if reported_at > now.replace(tzinfo=None):
        raise HTTPException(
            status_code=422,
            detail="reported_at cannot be in the future",
        )

    db_report = Report(
        report_type=report.report_type,
        title=report.title,
        description=report.description,
        category=report.category,
        color=report.color,
        location=report.location,
        reported_at=reported_at,
        created_at=datetime.utcnow(),
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/reports", response_model=ReportListResponse)
def list_reports(
    type: Optional[str] = Query(None, description="Filter by 'lost' or 'found'"),
    db: Session = Depends(get_db),
):
    """List all reports, optionally filtered by type."""
    query = db.query(Report)

    if type is not None:
        type_lower = type.lower().strip()
        if type_lower not in ("lost", "found"):
            raise HTTPException(
                status_code=422,
                detail="type must be 'lost' or 'found'",
            )
        query = query.filter(Report.report_type == type_lower)

    reports = query.order_by(Report.created_at.desc()).all()
    return ReportListResponse(reports=reports, count=len(reports))


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get a single report by ID."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
