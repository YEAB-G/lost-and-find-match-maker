from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ReportCreate(BaseModel):
    """Schema for creating a new report."""

    report_type: str = Field(..., description="'lost' or 'found'")
    title: str = Field(..., min_length=1, max_length=200, description="Item title")
    description: str = Field(..., min_length=1, description="Item description")
    category: Optional[str] = Field(
        None, max_length=100, description="Item category (optional)"
    )
    color: Optional[str] = Field(
        None, max_length=50, description="Item color (optional)"
    )
    location: str = Field(
        ..., min_length=1, max_length=200, description="Location"
    )
    reported_at: datetime = Field(..., description="When item was lost/found")

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ("lost", "found"):
            raise ValueError("report_type must be 'lost' or 'found'")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title cannot be empty or whitespace-only")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("description cannot be empty or whitespace-only")
        return v

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("location cannot be empty or whitespace-only")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class ReportResponse(BaseModel):
    """Schema for report responses."""

    id: int
    report_type: str
    title: str
    description: str
    category: Optional[str]
    color: Optional[str]
    location: str
    reported_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    """Schema for list of reports response."""

    reports: list[ReportResponse]
    count: int
