"""
Tests for the matches endpoint.

Tests all 5 verification scenarios:
1. A report with strong matches
2. A report with several matches and verify sorting
3. A report with no qualifying matches
4. A missing report ID
5. A system with no opposite-type reports
"""

from datetime import datetime


def create_report(client, **kwargs) -> dict:
    """Helper to create a report and return the response."""
    response = client.post("/reports", json=kwargs)
    assert response.status_code == 201
    return response.json()


# ============================================================================
# TEST 1: Report with Strong Matches
# ============================================================================


class TestStrongMatches:
    def test_report_with_strong_match(self, client):
        """
        Test 1: A report with strong matches.

        Create a lost report and a very similar found report.
        The match should be strong.
        """
        lost = create_report(
            client,
            report_type="lost",
            title="Black AirPods Case",
            description="Lost my black AirPods case near the cafeteria",
            category="electronics",
            color="black",
            location="cafeteria",
            reported_at="2024-01-15T10:00:00",
        )

        found = create_report(
            client,
            report_type="found",
            title="Black AirPods Case",
            description="Found black AirPods case near the cafeteria",
            category="electronics",
            color="black",
            location="cafeteria",
            reported_at="2024-01-15T14:00:00",
        )

        response = client.get(f"/reports/{lost['id']}/matches")
        assert response.status_code == 200

        data = response.json()
        assert data["report"]["id"] == lost["id"]
        assert data["total_candidates"] == 1
        assert data["qualifying_matches"] >= 1

        # Verify the match details
        match = data["matches"][0]
        assert match["matched_report"]["id"] == found["id"]
        assert match["score"] >= 80
        assert match["strength"] in ("strong", "possible")
        assert len(match["reasons"]) > 0
        assert "description" in match["factor_scores"]
        assert "category" in match["factor_scores"]
        assert "color" in match["factor_scores"]
        assert "location" in match["factor_scores"]
        assert "time" in match["factor_scores"]

    def test_response_structure(self, client):
        """Verify the response structure is complete and correct."""
        lost = create_report(
            client,
            report_type="lost",
            title="Blue Book",
            description="Lost blue book",
            category="documents",
            color="blue",
            location="library",
            reported_at="2024-01-15T10:00:00",
        )

        create_report(
            client,
            report_type="found",
            title="Blue Book",
            description="Found blue book",
            category="documents",
            color="blue",
            location="library",
            reported_at="2024-01-15T12:00:00",
        )

        response = client.get(f"/reports/{lost['id']}/matches")
        data = response.json()

        # Verify top-level structure
        assert "report" in data
        assert "matches" in data
        assert "total_candidates" in data
        assert "qualifying_matches" in data

        # Verify report structure
        report = data["report"]
        assert "id" in report
        assert "report_type" in report
        assert "title" in report
        assert "description" in report

        # Verify match structure
        match = data["matches"][0]
        assert "matched_report" in match
        assert "score" in match
        assert "strength" in match
        assert "reasons" in match
        assert "factor_scores" in match


# ============================================================================
# TEST 2: Several Matches and Sorting
# ============================================================================


class TestMultipleMatches:
    def test_matches_sorted_by_score(self, client):
        """
        Test 2: A report with several matches, verify sorting.

        Create a lost report and multiple found reports with varying similarity.
        Matches should be sorted from highest to lowest score.
        """
        lost = create_report(
            client,
            report_type="lost",
            title="Black Backpack",
            description="Lost my black backpack near the library",
            category="bags",
            color="black",
            location="library",
            reported_at="2024-01-15T10:00:00",
        )

        # Very similar (should score highest)
        similar = create_report(
            client,
            report_type="found",
            title="Black Backpack",
            description="Found black backpack near library",
            category="bags",
            color="black",
            location="library",
            reported_at="2024-01-15T11:00:00",
        )

        # Somewhat similar (should score middle)
        related = create_report(
            client,
            report_type="found",
            title="Dark Backpack",
            description="Found dark backpack at main library",
            category="bags",
            color="dark",
            location="main library",
            reported_at="2024-01-15T16:00:00",
        )

        # Unrelated (should score lowest or be filtered)
        create_report(
            client,
            report_type="found",
            title="Red Notebook",
            description="Found red notebook in cafeteria",
            category="documents",
            color="red",
            location="cafeteria",
            reported_at="2024-01-20T14:00:00",
        )

        response = client.get(f"/reports/{lost['id']}/matches")
        data = response.json()

        # Should have at least 2 qualifying matches
        assert data["qualifying_matches"] >= 2

        # Verify sorting: first match should have higher score
        matches = data["matches"]
        for i in range(len(matches) - 1):
            assert matches[i]["score"] >= matches[i + 1]["score"], (
                f"Match {i} score {matches[i]['score']} should be >= "
                f"match {i + 1} score {matches[i + 1]['score']}"
            )

        # The most similar should be first
        assert matches[0]["matched_report"]["id"] == similar["id"]

    def test_total_candidates_count(self, client):
        """Verify total_candidates counts all opposite-type reports."""
        lost = create_report(
            client,
            report_type="lost",
            title="Test Item",
            description="Test description",
            location="Library",
            reported_at="2024-01-15T10:00:00",
        )

        # Create 3 found reports
        for i in range(3):
            create_report(
                client,
                report_type="found",
                title=f"Found Item {i}",
                description=f"Found item {i}",
                location="Library",
                reported_at="2024-01-15T12:00:00",
            )

        response = client.get(f"/reports/{lost['id']}/matches")
        data = response.json()

        assert data["total_candidates"] == 3


# ============================================================================
# TEST 3: No Qualifying Matches
# ============================================================================


class TestNoQualifyingMatches:
    def test_no_qualifying_matches(self, client):
        """
        Test 3: A report with no qualifying matches.

        Create a lost report and a very different found report.
        No matches should qualify (all below threshold).
        """
        lost = create_report(
            client,
            report_type="lost",
            title="Blue Laptop",
            description="Lost my blue laptop in the engineering building",
            category="electronics",
            color="blue",
            location="engineering building",
            reported_at="2024-01-15T10:00:00",
        )

        # Very different found report
        create_report(
            client,
            report_type="found",
            title="Red Wallet",
            description="Found a red wallet at the football field",
            category="accessories",
            color="red",
            location="football field",
            reported_at="2024-01-25T14:00:00",
        )

        response = client.get(f"/reports/{lost['id']}/matches")
        data = response.json()

        assert data["total_candidates"] == 1
        assert data["qualifying_matches"] == 0
        assert len(data["matches"]) == 0

    def test_empty_matches_list(self, client):
        """Verify matches is an empty list when nothing qualifies."""
        lost = create_report(
            client,
            report_type="lost",
            title="Unique Item",
            description="Something very specific",
            location="Remote Building",
            reported_at="2024-01-15T10:00:00",
        )

        create_report(
            client,
            report_type="found",
            title="Different Item",
            description="Completely different thing",
            location="Another Building",
            reported_at="2024-01-20T10:00:00",
        )

        response = client.get(f"/reports/{lost['id']}/matches")
        data = response.json()

        assert isinstance(data["matches"], list)
        assert len(data["matches"]) == 0


# ============================================================================
# TEST 4: Missing Report ID
# ============================================================================


class TestMissingReport:
    def test_missing_report_returns_404(self, client):
        """
        Test 4: A missing report ID should return 404.
        """
        response = client.get("/reports/999/matches")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_nonexistent_report_with_candidates(self, client):
        """404 should be returned even if there are candidates in the system."""
        # Create some reports
        create_report(
            client,
            report_type="lost",
            title="Test",
            description="Test",
            location="Library",
            reported_at="2024-01-15T10:00:00",
        )
        create_report(
            client,
            report_type="found",
            title="Test",
            description="Test",
            location="Library",
            reported_at="2024-01-15T10:00:00",
        )

        response = client.get("/reports/999/matches")
        assert response.status_code == 404


# ============================================================================
# TEST 5: No Opposite-Type Reports
# ============================================================================


class TestNoOppositeType:
    def test_no_opposite_type_reports(self, client):
        """
        Test 5: A system with no opposite-type reports.

        Create only lost reports. A lost report should have 0 candidates.
        """
        lost = create_report(
            client,
            report_type="lost",
            title="Black Backpack",
            description="Lost my black backpack",
            location="Library",
            reported_at="2024-01-15T10:00:00",
        )

        # Create more lost reports (same type, not candidates)
        create_report(
            client,
            report_type="lost",
            title="Blue Book",
            description="Lost blue book",
            location="Library",
            reported_at="2024-01-15T11:00:00",
        )

        response = client.get(f"/reports/{lost['id']}/matches")
        data = response.json()

        assert data["total_candidates"] == 0
        assert data["qualifying_matches"] == 0
        assert len(data["matches"]) == 0

    def test_found_report_with_no_lost_reports(self, client):
        """A found report should work correctly when no lost reports exist."""
        found = create_report(
            client,
            report_type="found",
            title="Blue Book",
            description="Found blue book",
            location="Library",
            reported_at="2024-01-15T12:00:00",
        )

        response = client.get(f"/reports/{found['id']}/matches")
        data = response.json()

        assert data["report"]["id"] == found["id"]
        assert data["total_candidates"] == 0
        assert len(data["matches"]) == 0


# ============================================================================
# ADDITIONAL TESTS
# ============================================================================


class TestAdditionalScenarios:
    def test_only_opposite_type_compared(self, client):
        """Verify that only opposite-type reports are compared."""
        lost = create_report(
            client,
            report_type="lost",
            title="Black Case",
            description="Lost black case",
            location="Library",
            reported_at="2024-01-15T10:00:00",
        )

        # Same type (should NOT be a candidate)
        create_report(
            client,
            report_type="lost",
            title="Black Case",
            description="Lost black case",
            location="Library",
            reported_at="2024-01-15T10:00:00",
        )

        # Opposite type (should be a candidate)
        create_report(
            client,
            report_type="found",
            title="Black Case",
            description="Found black case",
            location="Library",
            reported_at="2024-01-15T10:00:00",
        )

        response = client.get(f"/reports/{lost['id']}/matches")
        data = response.json()

        # Should only have 1 candidate (the found report)
        assert data["total_candidates"] == 1

    def test_found_report_matches_lost_reports(self, client):
        """Verify that a found report can match against lost reports."""
        found = create_report(
            client,
            report_type="found",
            title="Black Case",
            description="Found black case near cafeteria",
            category="electronics",
            color="black",
            location="cafeteria",
            reported_at="2024-01-15T14:00:00",
        )

        create_report(
            client,
            report_type="lost",
            title="Black Case",
            description="Lost black case near cafeteria",
            category="electronics",
            color="black",
            location="cafeteria",
            reported_at="2024-01-15T10:00:00",
        )

        response = client.get(f"/reports/{found['id']}/matches")
        data = response.json()

        assert data["report"]["report_type"] == "found"
        assert data["total_candidates"] == 1
        assert data["qualifying_matches"] >= 1

    def test_match_includes_all_factor_scores(self, client):
        """Verify that all factor scores are included in the response."""
        lost = create_report(
            client,
            report_type="lost",
            title="Black Case",
            description="Lost black case",
            category="electronics",
            color="black",
            location="library",
            reported_at="2024-01-15T10:00:00",
        )

        create_report(
            client,
            report_type="found",
            title="Black Case",
            description="Found black case",
            category="electronics",
            color="black",
            location="library",
            reported_at="2024-01-15T12:00:00",
        )

        response = client.get(f"/reports/{lost['id']}/matches")
        data = response.json()

        match = data["matches"][0]
        factor_scores = match["factor_scores"]

        # All 5 factors should be present
        assert "description" in factor_scores
        assert "category" in factor_scores
        assert "color" in factor_scores
        assert "location" in factor_scores
        assert "time" in factor_scores

    def test_match_reasons_are_meaningful(self, client):
        """Verify that reasons are non-empty and descriptive."""
        lost = create_report(
            client,
            report_type="lost",
            title="Blue Backpack",
            description="Lost blue backpack near library",
            category="bags",
            color="blue",
            location="library",
            reported_at="2024-01-15T10:00:00",
        )

        create_report(
            client,
            report_type="found",
            title="Blue Backpack",
            description="Found blue backpack at library",
            category="bags",
            color="blue",
            location="library",
            reported_at="2024-01-15T12:00:00",
        )

        response = client.get(f"/reports/{lost['id']}/matches")
        data = response.json()

        match = data["matches"][0]
        assert len(match["reasons"]) > 0

        for reason in match["reasons"]:
            assert isinstance(reason, str)
            assert len(reason) > 0
            # Reasons should be meaningful (not just "match found")
            assert len(reason) > 5
