"""
Tests for the matching engine.

These tests verify the matcher works independently of FastAPI routes.
"""

from datetime import datetime, timedelta

import pytest

from app.services.matcher import (
    Report,
    calculate_sequence_similarity,
    calculate_token_similarity,
    extract_tokens,
    match_reports,
    normalize_text,
    score_category,
    score_color,
    score_description,
    score_location,
    score_time,
)


def make_report(
    id: int = 1,
    report_type: str = "lost",
    title: str = "Test Item",
    description: str = "Test description",
    category: str | None = None,
    color: str | None = None,
    location: str = "Library",
    reported_at: datetime | None = None,
) -> Report:
    """Helper to create a test report."""
    if reported_at is None:
        reported_at = datetime(2024, 1, 15, 10, 0, 0)
    return Report(
        id=id,
        report_type=report_type,
        title=title,
        description=description,
        category=category,
        color=color,
        location=location,
        reported_at=reported_at,
        created_at=datetime.now(),
    )


# ============================================================================
# TEXT PROCESSING TESTS
# ============================================================================


class TestTextProcessing:
    def test_normalize_text_lowercase(self):
        assert normalize_text("Hello World") == "hello world"

    def test_normalize_text_punctuation(self):
        assert normalize_text("Hello, World!") == "hello world"

    def test_normalize_text_whitespace(self):
        assert normalize_text("  Hello   World  ") == "hello world"

    def test_normalize_text_empty(self):
        assert normalize_text("") == ""

    def test_extract_tokens(self):
        tokens = extract_tokens("Black AirPods Case")
        assert "black" in tokens
        assert "airpods" in tokens
        assert "case" in tokens

    def test_extract_tokens_filters_short(self):
        tokens = extract_tokens("A big dog")
        assert "a" not in tokens  # filtered out (length 1)
        assert "big" in tokens
        assert "dog" in tokens

    def test_calculate_token_similarity_identical(self):
        sim = calculate_token_similarity("black case", "black case")
        assert sim == 1.0

    def test_calculate_token_similarity_no_overlap(self):
        sim = calculate_token_similarity("red book", "blue pen")
        assert sim == 0.0

    def test_calculate_token_similarity_partial(self):
        sim = calculate_token_similarity("black case", "black box")
        # intersection: {black}, union: {black, case, box}
        expected = 1 / 3
        assert abs(sim - expected) < 0.01

    def test_calculate_sequence_similarity_identical(self):
        sim = calculate_sequence_similarity("black case", "black case")
        assert sim == 1.0

    def test_calculate_sequence_similarity_different(self):
        sim = calculate_sequence_similarity("hello world", "goodbye universe")
        assert sim < 0.5


# ============================================================================
# DESCRIPTION SCORING TESTS
# ============================================================================


class TestDescriptionScoring:
    def test_identical_descriptions(self):
        score = score_description(
            "Black Case", "Lost black case",
            "Black Case", "Found black case"
        )
        # Should be reasonably high (token similarity + sequence similarity)
        assert score >= 20

    def test_similar_descriptions(self):
        score = score_description(
            "Black AirPods", "Lost wireless earbuds",
            "Dark Earbuds", "Found wireless earbuds"
        )
        assert score > 10  # Should have some match

    def test_unrelated_descriptions(self):
        score = score_description(
            "Blue Book", "Lost chemistry textbook",
            "Red Keys", "Found car keys"
        )
        assert score < 15  # Should be low

    def test_empty_descriptions(self):
        score = score_description("", "", "", "")
        assert score == 0.0


# ============================================================================
# CATEGORY SCORING TESTS
# ============================================================================


class TestCategoryScoring:
    def test_exact_match(self):
        score = score_category("electronics", "electronics")
        assert score == 20.0

    def test_case_insensitive(self):
        score = score_category("Electronics", "ELECTRONICS")
        assert score == 20.0

    def test_no_match(self):
        score = score_category("electronics", "clothing")
        assert score == 0.0

    def test_missing_category(self):
        score = score_category(None, "electronics")
        assert score is None

    def test_both_missing(self):
        score = score_category(None, None)
        assert score is None


# ============================================================================
# COLOR SCORING TESTS
# ============================================================================


class TestColorScoring:
    def test_exact_match(self):
        score = score_color("black", "black")
        assert score == 15.0

    def test_equivalent_colors(self):
        score = score_color("grey", "gray")
        assert score == 15.0

    def test_related_colors(self):
        score = score_color("black", "dark")
        assert score >= 10.0  # At least 70% of 15

    def test_unrelated_colors(self):
        score = score_color("red", "blue")
        assert score == 0.0

    def test_missing_color(self):
        score = score_color(None, "black")
        assert score is None

    def test_both_missing(self):
        score = score_color(None, None)
        assert score is None

    def test_blue_navy_related(self):
        score = score_color("blue", "navy")
        assert score >= 10.0

    def test_red_maroon_related(self):
        score = score_color("red", "maroon")
        assert score >= 10.0


# ============================================================================
# LOCATION SCORING TESTS
# ============================================================================


class TestLocationScoring:
    def test_exact_match(self):
        score = score_location("library", "library")
        assert score == 15.0

    def test_related_locations(self):
        score = score_location("cafeteria", "coffee shop")
        assert score >= 10.0  # At least 70% of 15

    def test_unrelated_locations(self):
        score = score_location("library", "gym")
        assert score == 0.0

    def test_substring_match(self):
        score = score_location("library", "main library")
        assert score >= 7.0  # At least 50% of 15

    def test_case_insensitive(self):
        score = score_location("Library", "library")
        assert score == 15.0


# ============================================================================
# TIME SCORING TESTS
# ============================================================================


class TestTimeScoring:
    def test_same_day(self):
        dt1 = datetime(2024, 1, 15, 10, 0, 0)
        dt2 = datetime(2024, 1, 15, 14, 0, 0)
        score = score_time(dt1, dt2)
        assert score == 10.0

    def test_within_one_day(self):
        dt1 = datetime(2024, 1, 15, 10, 0, 0)
        dt2 = datetime(2024, 1, 15, 20, 0, 0)  # Same day, different time
        score = score_time(dt1, dt2)
        assert score == 10.0  # Same day = full score

    def test_within_three_days(self):
        dt1 = datetime(2024, 1, 15, 10, 0, 0)
        dt2 = datetime(2024, 1, 17, 14, 0, 0)
        score = score_time(dt1, dt2)
        assert score == 5.0  # 50% of 10

    def test_within_seven_days(self):
        dt1 = datetime(2024, 1, 15, 10, 0, 0)
        dt2 = datetime(2024, 1, 20, 14, 0, 0)
        score = score_time(dt1, dt2)
        assert score == 2.0  # 20% of 10

    def test_more_than_seven_days(self):
        dt1 = datetime(2024, 1, 15, 10, 0, 0)
        dt2 = datetime(2024, 1, 25, 14, 0, 0)
        score = score_time(dt1, dt2)
        assert score == 0.0


# ============================================================================
# MAIN MATCHER TESTS
# ============================================================================


class TestMatcher:
    def test_strong_match_airpods(self):
        """Test strong match between similar lost and found reports."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Black AirPods Case",
            description="Lost black AirPods case near cafeteria",
            category="electronics",
            color="black",
            location="cafeteria",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Black AirPods Case",
            description="Found black AirPods case near cafeteria",
            category="electronics",
            color="black",
            location="cafeteria",
            reported_at=datetime(2024, 1, 15, 14, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        assert result.score >= 80
        assert len(result.reasons) > 0
        print(f"Strong match score: {result.score}")
        print(f"Reasons: {result.reasons}")

    def test_related_locations(self):
        """Test similar backpack near related library locations."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Blue Backpack",
            description="Lost my blue backpack in the library",
            category="bags",
            color="blue",
            location="library",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Blue Backpack",
            description="Found a blue backpack at the main library entrance",
            category="bags",
            color="navy",
            location="main library",
            reported_at=datetime(2024, 1, 15, 16, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        assert result.score >= 70
        print(f"Related locations score: {result.score}")

    def test_unrelated_items(self):
        """Test clearly unrelated items."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Blue Chemistry Textbook",
            description="Lost my chemistry textbook with notes",
            category="documents",
            color="blue",
            location="library",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Red Car Keys",
            description="Found red car keys in the parking lot",
            category="keys",
            color="red",
            location="parking lot",
            reported_at=datetime(2024, 1, 20, 14, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        assert result.strength == "below_threshold"
        assert result.score < 40
        print(f"Unrelated items score: {result.score}")

    def test_missing_category(self):
        """Test matching when category is missing."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Black Case",
            description="Lost a black case",
            category=None,
            color="black",
            location="library",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Black Case",
            description="Found a black case",
            category="electronics",
            color="black",
            location="library",
            reported_at=datetime(2024, 1, 15, 12, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        assert result.factor_available["category"] is False
        assert result.factor_scores["category"] is None
        # Score should be normalized against available points
        assert result.available_points == 80  # 40 + 15 + 15 + 10 (no category)
        print(f"Missing category score: {result.score}")

    def test_missing_color(self):
        """Test matching when color is missing."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Wireless Earbuds",
            description="Lost my wireless earbuds",
            category="electronics",
            color=None,
            location="cafeteria",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Wireless Earbuds",
            description="Found wireless earbuds",
            category="electronics",
            color="white",
            location="cafeteria",
            reported_at=datetime(2024, 1, 15, 11, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        assert result.factor_available["color"] is False
        assert result.factor_scores["color"] is None
        assert result.available_points == 85  # 40 + 20 + 15 + 10 (no color)
        print(f"Missing color score: {result.score}")

    def test_time_distance(self):
        """Test reports far apart in time."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Black Case",
            description="Lost a black case",
            category="electronics",
            color="black",
            location="library",
            reported_at=datetime(2024, 1, 10, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Black Case",
            description="Found a black case",
            category="electronics",
            color="black",
            location="library",
            reported_at=datetime(2024, 1, 25, 14, 0, 0),  # 15 days later
        )

        result = match_reports(lost, found)

        assert result is not None
        assert result.factor_scores["time"] == 0.0
        print(f"Time distance score: {result.score}")

    def test_same_type_rejected(self):
        """Test that same report types are rejected."""
        lost1 = make_report(id=1, report_type="lost")
        lost2 = make_report(id=2, report_type="lost")

        result = match_reports(lost1, lost2)

        assert result is None

    def test_found_first_order(self):
        """Test that found reports can be first (order doesn't matter)."""
        found = make_report(
            id=1,
            report_type="found",
            title="Black Case",
            description="Found a black case",
            category="electronics",
            color="black",
            location="library",
        )
        lost = make_report(
            id=2,
            report_type="lost",
            title="Black Case",
            description="Lost a black case",
            category="electronics",
            color="black",
            location="library",
        )

        result = match_reports(found, lost)

        assert result is not None
        assert result.score > 80

    def test_reasons_generated(self):
        """Test that meaningful reasons are generated."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Blue Book",
            description="Lost a blue textbook",
            category="documents",
            color="blue",
            location="library",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Blue Book",
            description="Found a blue textbook",
            category="documents",
            color="blue",
            location="library",
            reported_at=datetime(2024, 1, 15, 12, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        assert len(result.reasons) > 0
        # Check for specific reasons
        reasons_text = " ".join(result.reasons).lower()
        assert "description" in reasons_text or "similar" in reasons_text
        print(f"Reasons: {result.reasons}")


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestEdgeCases:
    def test_empty_descriptions(self):
        """Test matching with empty descriptions."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Black Case",
            description="",
            location="library",
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Black Case",
            description="",
            location="library",
        )

        result = match_reports(lost, found)

        assert result is not None
        # Empty descriptions should still have some title match
        assert result.factor_scores["description"] >= 0

    def test_whitespace_only_fields(self):
        """Test handling of whitespace-only fields."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="  ",
            description="  ",
            location="library",
        )
        found = make_report(
            id=2,
            report_type="found",
            title="  ",
            description="  ",
            location="library",
        )

        result = match_reports(lost, found)

        assert result is not None

    def test_score_normalization_accuracy(self):
        """Test that score normalization works correctly."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Blue Book",
            description="Lost a blue textbook",
            category="documents",
            color="blue",
            location="library",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Blue Book",
            description="Found a blue textbook",
            category="documents",
            color="blue",
            location="library",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        # High match due to similar reports
        assert result.score >= 85
        assert result.available_points == 100  # All factors available
        # Earned points should be close to available
        assert result.earned_points >= 85
