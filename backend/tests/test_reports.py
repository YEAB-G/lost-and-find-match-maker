from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient


def test_create_lost_report(client):
    """Test creating a lost item report."""
    response = client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "Black AirPods Case",
            "description": "I lost my black AirPods case near the cafeteria",
            "category": "electronics",
            "color": "black",
            "location": "cafeteria",
            "reported_at": "2024-01-15T10:30:00",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["report_type"] == "lost"
    assert data["title"] == "Black AirPods Case"
    assert "id" in data
    assert "created_at" in data


def test_create_found_report(client):
    """Test creating a found item report."""
    response = client.post(
        "/reports",
        json={
            "report_type": "found",
            "title": "Wireless Earbud Case",
            "description": "Found a dark wireless earbud case beside the coffee shop",
            "category": "electronics",
            "color": "dark",
            "location": "coffee shop",
            "reported_at": "2024-01-15T14:00:00",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["report_type"] == "found"


def test_create_report_without_optional_fields(client):
    """Test creating a report without optional category and color."""
    response = client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "Blue Notebook",
            "description": "Lost a blue notebook",
            "location": "library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["category"] is None
    assert data["color"] is None


def test_reject_empty_title(client):
    """Test that empty title is rejected."""
    response = client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "",
            "description": "Some description",
            "location": "library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )
    assert response.status_code == 422


def test_reject_whitespace_only_title(client):
    """Test that whitespace-only title is rejected."""
    response = client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "   ",
            "description": "Some description",
            "location": "library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )
    assert response.status_code == 422


def test_reject_empty_description(client):
    """Test that empty description is rejected."""
    response = client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "Title",
            "description": "",
            "location": "library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )
    assert response.status_code == 422


def test_reject_empty_location(client):
    """Test that empty location is rejected."""
    response = client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "Title",
            "description": "Some description",
            "location": "",
            "reported_at": "2024-01-15T09:00:00",
        },
    )
    assert response.status_code == 422


def test_reject_invalid_report_type(client):
    """Test that invalid report type is rejected."""
    response = client.post(
        "/reports",
        json={
            "report_type": "maybe",
            "title": "Title",
            "description": "Some description",
            "location": "library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )
    assert response.status_code == 422


def test_reject_future_reported_at(client):
    """Test that future reported_at is rejected."""
    future_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    response = client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "Title",
            "description": "Some description",
            "location": "library",
            "reported_at": future_date,
        },
    )
    assert response.status_code == 422
    assert "future" in response.json()["detail"].lower()


def test_reject_missing_required_fields(client):
    """Test that missing required fields are rejected."""
    response = client.post(
        "/reports",
        json={
            "report_type": "lost",
        },
    )
    assert response.status_code == 422


def test_list_reports(client):
    """Test listing all reports."""
    # Create some reports
    client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "Lost Item 1",
            "description": "Description 1",
            "location": "Library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )
    client.post(
        "/reports",
        json={
            "report_type": "found",
            "title": "Found Item 1",
            "description": "Description 2",
            "location": "Cafeteria",
            "reported_at": "2024-01-15T10:00:00",
        },
    )

    response = client.get("/reports")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["reports"]) == 2


def test_list_reports_filter_by_lost(client):
    """Test filtering reports by lost type."""
    client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "Lost Item",
            "description": "Description",
            "location": "Library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )
    client.post(
        "/reports",
        json={
            "report_type": "found",
            "title": "Found Item",
            "description": "Description",
            "location": "Library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )

    response = client.get("/reports?type=lost")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["reports"][0]["report_type"] == "lost"


def test_list_reports_filter_by_found(client):
    """Test filtering reports by found type."""
    client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "Lost Item",
            "description": "Description",
            "location": "Library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )
    client.post(
        "/reports",
        json={
            "report_type": "found",
            "title": "Found Item",
            "description": "Description",
            "location": "Library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )

    response = client.get("/reports?type=found")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["reports"][0]["report_type"] == "found"


def test_list_reports_invalid_filter(client):
    """Test that invalid filter type is rejected."""
    response = client.get("/reports?type=maybe")
    assert response.status_code == 422


def test_get_report_by_id(client):
    """Test getting a single report by ID."""
    # Create a report
    create_response = client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "My Report",
            "description": "Description",
            "location": "Library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )
    report_id = create_response.json()["id"]

    # Get the report
    response = client.get(f"/reports/{report_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == report_id
    assert data["title"] == "My Report"


def test_get_report_not_found(client):
    """Test that 404 is returned for non-existent report."""
    response = client.get("/reports/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_reports_ordered_by_newest(client):
    """Test that reports are ordered by newest first."""
    # Create reports with different timestamps
    client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "Older Report",
            "description": "Description",
            "location": "Library",
            "reported_at": "2024-01-14T09:00:00",
        },
    )
    client.post(
        "/reports",
        json={
            "report_type": "lost",
            "title": "Newer Report",
            "description": "Description",
            "location": "Library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )

    response = client.get("/reports")
    data = response.json()
    assert data["reports"][0]["title"] == "Newer Report"
    assert data["reports"][1]["title"] == "Older Report"


def test_report_type_case_insensitive(client):
    """Test that report type is case insensitive."""
    response = client.post(
        "/reports",
        json={
            "report_type": "Lost",
            "title": "Title",
            "description": "Description",
            "location": "Library",
            "reported_at": "2024-01-15T09:00:00",
        },
    )
    assert response.status_code == 201
    assert response.json()["report_type"] == "lost"
