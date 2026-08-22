"""
Phase 4: Matching Engine Tests

Comprehensive tests for the matching engine covering all required scenarios.
Tests are organized by the 8 required test scenarios plus additional edge cases.
"""

from datetime import datetime, timedelta

import pytest

from app.services.matcher import (
    Report,
    match_reports,
    score_category,
    score_color,
    score_description,
    score_location,
    score_time,
)


# ============================================================================
# TEST HELPERS
# ============================================================================


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
    """Helper to create a test report with sensible defaults."""
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
        created_at=datetime(2024, 1, 15, 10, 0, 0),
    )


# ============================================================================
# TEST 1: STRONG MATCH
# Lost: Black AirPods case near cafeteria
# Found: Dark wireless earbud case near coffee shop
# ============================================================================


class TestStrongMatch:
    def test_airpods_case_strong_match(self):
        """
        Test 1: Strong match between similar lost and found reports.

        Lost: Black AirPods case near cafeteria
        Found: Dark wireless earbud case near coffee shop

        Should produce a relatively high score due to:
        - Similar descriptions (AirPods, case, earbud, wireless)
        - Related colors (black, dark)
        - Related locations (cafeteria, coffee shop)
        - Same day
        """
        lost = make_report(
            id=1,
            report_type="lost",
            title="Black AirPods Case",
            description="I lost my black AirPods case near the cafeteria",
            category="electronics",
            color="black",
            location="cafeteria",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Wireless Earbud Case",
            description="Found a dark wireless earbud case near the coffee shop",
            category="electronics",
            color="dark",
            location="coffee shop",
            reported_at=datetime(2024, 1, 15, 14, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        # Related colors, related locations, and different descriptions
        # produce a score in the possible range (60-79)
        assert result.score >= 60, f"Expected score >= 60, got {result.score}"
        assert result.strength in ("strong", "possible")
        assert len(result.reasons) >= 3, "Expected at least 3 reasons"
        assert result.factor_available["category"] is True
        assert result.factor_available["color"] is True
        assert result.factor_available["location"] is True
        assert result.factor_available["time"] is True
        # Verify related factors got partial credit
        assert result.factor_scores["color"] > 0, "Related colors should score > 0"
        assert result.factor_scores["location"] > 0, "Related locations should score > 0"

    def test_high_description_score_for_similar_items(self):
        """Verify description scoring gives high marks for similar items."""
        lost = make_report(
            title="Black AirPods Case",
            description="Lost black AirPods case near cafeteria",
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Black AirPods Case",
            description="Found black AirPods case near cafeteria",
        )

        score = score_description(
            lost.title, lost.description,
            found.title, found.description,
        )
        assert score >= 30, f"Expected description score >= 30, got {score}"


# ============================================================================
# TEST 2: RELATED BACKPACK REPORTS
# Lost: Black backpack near library
# Found: Dark backpack at library entrance
# ============================================================================


class TestRelatedBackpackMatch:
    def test_related_backpack_match(self):
        """
        Test 2: Related backpack reports.

        Lost: Black backpack near library
        Found: Dark backpack at library entrance

        Should be strong or possible match due to:
        - Same item type (backpack)
        - Related colors (black, dark)
        - Related locations (library, library entrance)
        - Same day
        """
        lost = make_report(
            id=1,
            report_type="lost",
            title="Black Backpack",
            description="Lost my black backpack near the library",
            category="bags",
            color="black",
            location="library",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Dark Backpack",
            description="Found a dark backpack at the library entrance",
            category="bags",
            color="dark",
            location="library entrance",
            reported_at=datetime(2024, 1, 15, 16, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        # Related colors and related locations with similar descriptions
        assert result.score >= 60, f"Expected score >= 60, got {result.score}"
        assert result.strength in ("strong", "possible")

        # Verify location similarity is recognized
        assert result.factor_scores["location"] > 0
        # Verify color similarity is recognized
        assert result.factor_scores["color"] > 0

    def test_related_location_scoring(self):
        """Verify related locations get partial credit."""
        score = score_location("library", "library entrance")
        assert score > 0, "Related locations should get partial credit"
        assert score < 15, "Related locations should not get full credit"

    def test_related_color_scoring(self):
        """Verify related colors get partial credit."""
        score = score_color("black", "dark")
        assert score > 0, "Related colors should get partial credit"
        assert score < 15, "Related colors should not get full credit"


# ============================================================================
# TEST 3: UNRELATED REPORTS
# Lost: Blue laptop in engineering building
# Found: Red wallet at football field two weeks later
# ============================================================================


class TestUnrelatedMatch:
    def test_unrelated_reports_below_threshold(self):
        """
        Test 3: Clearly unrelated reports should be below threshold.

        Lost: Blue laptop in engineering building
        Found: Red wallet at football field two weeks later

        Should be below threshold due to:
        - Different items (laptop vs wallet)
        - Different categories (electronics vs accessories)
        - Different colors (blue vs red)
        - Different locations (engineering building vs football field)
        - Different times (two weeks apart)
        """
        lost = make_report(
            id=1,
            report_type="lost",
            title="Blue Laptop",
            description="Lost my blue laptop in the engineering building",
            category="electronics",
            color="blue",
            location="engineering building",
            reported_at=datetime(2024, 1, 10, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Red Wallet",
            description="Found a red wallet at the football field",
            category="accessories",
            color="red",
            location="football field",
            reported_at=datetime(2024, 1, 24, 14, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        assert result.score < 40, f"Expected score < 40, got {result.score}"
        assert result.strength == "below_threshold"
        assert result.factor_scores["time"] == 0.0

    def test_different_categories_score_zero(self):
        """Verify different categories score zero."""
        score = score_category("electronics", "accessories")
        assert score == 0.0

    def test_different_colors_score_zero(self):
        """Verify different colors score zero."""
        score = score_color("blue", "red")
        assert score == 0.0

    def test_different_locations_score_zero(self):
        """Verify different locations score zero."""
        score = score_location("engineering building", "football field")
        assert score == 0.0


# ============================================================================
# TEST 4: MISSING OPTIONAL DATA
# ============================================================================


class TestMissingOptionalData:
    def test_missing_category_normalized(self):
        """
        Test 4a: Missing category should not penalize the score.

        When category is missing from one report, the category factor
        should be excluded from available points, and the score
        should be normalized accordingly.
        """
        lost = make_report(
            id=1,
            report_type="lost",
            title="Black Case",
            description="Lost a black case",
            category=None,  # Missing
            color="black",
            location="cafeteria",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Black Case",
            description="Found a black case",
            category="electronics",
            color="black",
            location="cafeteria",
            reported_at=datetime(2024, 1, 15, 12, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        # Category factor should be excluded
        assert result.factor_available["category"] is False
        assert result.factor_scores["category"] is None
        # Available points should be 80 (100 - 20)
        assert result.available_points == 80
        # Score should be high since other factors match
        assert result.score >= 80

    def test_missing_color_normalized(self):
        """
        Test 4b: Missing color should not penalize the score.

        When color is missing from one report, the color factor
        should be excluded from available points.
        """
        lost = make_report(
            id=1,
            report_type="lost",
            title="Wireless Earbuds",
            description="Lost wireless earbuds",
            category="electronics",
            color=None,  # Missing
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
        # Available points should be 85 (100 - 15)
        assert result.available_points == 85
        # Score should be high since other factors match
        assert result.score >= 80

    def test_both_optional_fields_missing(self):
        """
        Test 4c: Both category and color missing.

        Available points should be 65 (100 - 20 - 15).
        Score should be normalized against 65 available points.
        """
        lost = make_report(
            id=1,
            report_type="lost",
            title="Black Case",
            description="Lost a black case",
            category=None,
            color=None,
            location="cafeteria",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Black Case",
            description="Found a black case",
            category=None,
            color=None,
            location="cafeteria",
            reported_at=datetime(2024, 1, 15, 12, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        assert result.factor_available["category"] is False
        assert result.factor_available["color"] is False
        assert result.available_points == 65
        # Score should still be meaningful
        assert result.score >= 70

    def test_missing_data_not_treated_as_mismatch(self):
        """
        Test 4d: Missing data must NOT automatically act as a mismatch.

        If both reports match on all available factors, the score
        should reflect that, not penalize for missing data.
        """
        lost = make_report(
            id=1,
            report_type="lost",
            title="Blue Book",
            description="Lost blue book at library",
            category=None,
            color=None,
            location="library",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Blue Book",
            description="Found blue book at library",
            category=None,
            color=None,
            location="library",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )

        result = match_reports(lost, found)

        assert result is not None
        # With only description, location, and time (65 available points)
        # and all matching, score should be high
        assert result.score >= 80, (
            f"Missing data should not penalize. Got {result.score}"
        )

    def test_missing_category_in_one_report(self):
        """Test with category present in one report but not the other."""
        cat_score = score_category(None, "electronics")
        assert cat_score is None, "Missing category should return None"

        # Both missing should also return None
        cat_score_both = score_category(None, None)
        assert cat_score_both is None

    def test_missing_color_in_one_report(self):
        """Test with color present in one report but not the other."""
        color_score = score_color(None, "black")
        assert color_score is None, "Missing color should return None"

        # Both missing should also return None
        color_score_both = score_color(None, None)
        assert color_score_both is None


# ============================================================================
# TEST 5: SAME REPORT TYPE
# ============================================================================


class TestSameReportType:
    def test_lost_to_lost_rejected(self):
        """
        Test 5a: Lost-to-lost comparisons must be rejected.

        The matcher should return None when comparing two reports
        of the same type.
        """
        lost1 = make_report(
            id=1,
            report_type="lost",
            title="Black Case",
            description="Lost black case",
        )
        lost2 = make_report(
            id=2,
            report_type="lost",
            title="Black Case",
            description="Found black case",
        )

        result = match_reports(lost1, lost2)
        assert result is None, "Lost-to-lost should return None"

    def test_found_to_found_rejected(self):
        """
        Test 5b: Found-to-found comparisons must be rejected.
        """
        found1 = make_report(
            id=1,
            report_type="found",
            title="Blue Book",
            description="Found blue book",
        )
        found2 = make_report(
            id=2,
            report_type="found",
            title="Blue Book",
            description="Found another blue book",
        )

        result = match_reports(found1, found2)
        assert result is None, "Found-to-found should return None"

    def test_lost_to_found_accepted(self):
        """
        Test 5c: Lost-to-found comparisons should work.
        """
        lost = make_report(
            id=1,
            report_type="lost",
            title="Blue Book",
            description="Lost blue book",
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Blue Book",
            description="Found blue book",
        )

        result = match_reports(lost, found)
        assert result is not None, "Lost-to-found should return a result"

    def test_found_to_lost_accepted(self):
        """
        Test 5d: Found-to-lost comparisons should also work (order doesn't matter).
        """
        found = make_report(
            id=1,
            report_type="found",
            title="Blue Book",
            description="Found blue book",
        )
        lost = make_report(
            id=2,
            report_type="lost",
            title="Blue Book",
            description="Lost blue book",
        )

        result = match_reports(found, lost)
        assert result is not None, "Found-to-lost should return a result"


# ============================================================================
# TEST 6: TIME PROXIMITY
# ============================================================================


class TestTimeProximity:
    def test_same_day_full_score(self):
        """
        Test 6a: Same day should give full time score.
        """
        dt1 = datetime(2024, 1, 15, 10, 0, 0)
        dt2 = datetime(2024, 1, 15, 18, 0, 0)
        score = score_time(dt1, dt2)
        assert score == 10.0, f"Same day should score 10.0, got {score}"

    def test_one_day_apart(self):
        """
        Test 6b: Reports less than 24 hours apart but different days.

        This tests the within-1-day bucket: different calendar dates
        but within 24 hours of each other.
        """
        dt1 = datetime(2024, 1, 15, 23, 0, 0)
        dt2 = datetime(2024, 1, 16, 8, 0, 0)  # 9 hours later, different day
        score = score_time(dt1, dt2)
        assert score == 8.0, f"Within 1 day should score 8.0, got {score}"

    def test_several_days_apart(self):
        """
        Test 6c: Reports several days apart should get medium score.
        """
        dt1 = datetime(2024, 1, 15, 10, 0, 0)
        dt2 = datetime(2024, 1, 17, 14, 0, 0)
        score = score_time(dt1, dt2)
        assert score == 5.0, f"2 days apart should score 5.0, got {score}"

    def test_more_than_seven_days_apart(self):
        """
        Test 6d: Reports more than 7 days apart should get zero time score.
        """
        dt1 = datetime(2024, 1, 10, 10, 0, 0)
        dt2 = datetime(2024, 1, 25, 14, 0, 0)
        score = score_time(dt1, dt2)
        assert score == 0.0, f">7 days should score 0.0, got {score}"

    def test_time_in_full_match_scenario(self):
        """Test time scoring within a full match context."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Black Case",
            description="Lost black case",
            category="electronics",
            color="black",
            location="cafeteria",
            reported_at=datetime(2024, 1, 10, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Black Case",
            description="Found black case",
            category="electronics",
            color="black",
            location="cafeteria",
            reported_at=datetime(2024, 1, 25, 14, 0, 0),
        )

        result = match_reports(lost, found)
        assert result is not None
        # Time factor is always available, even when score is 0
        assert result.factor_scores["time"] == 0.0
        assert result.factor_available["time"] is True
        # Available points is 100 because time IS available (just scored 0)
        assert result.available_points == 100
        # Score is lowered because earned points < 100
        assert result.score < 100

    def test_boundary_one_week(self):
        """Test exactly 7 days apart."""
        dt1 = datetime(2024, 1, 15, 10, 0, 0)
        dt2 = datetime(2024, 1, 22, 10, 0, 0)
        score = score_time(dt1, dt2)
        assert score == 2.0, f"Exactly 7 days should score 2.0, got {score}"


# ============================================================================
# TEST 7: COLOR NORMALIZATION
# ============================================================================


class TestColorNormalization:
    def test_grey_equals_gray(self):
        """
        Test 7a: grey and gray should be treated as the same color.
        """
        score = score_color("grey", "gray")
        assert score == 15.0, f"grey/gray should be equal, got {score}"

    def test_gray_equals_grey(self):
        """Reverse order should also work."""
        score = score_color("gray", "grey")
        assert score == 15.0

    def test_black_and_dark_related(self):
        """
        Test 7b: black and dark should be related (partial score).
        """
        score = score_color("black", "dark")
        assert score >= 10.0, f"black/dark should be related, got {score}"
        assert score < 15.0, f"black/dark should not be exact, got {score}"

    def test_blue_and_navy_related(self):
        """
        Test 7c: blue and navy should be related (partial score).
        """
        score = score_color("blue", "navy")
        assert score >= 10.0, f"blue/navy should be related, got {score}"
        assert score < 15.0, f"blue/navy should not be exact, got {score}"

    def test_red_and_maroon_related(self):
        """red and maroon should be related."""
        score = score_color("red", "maroon")
        assert score >= 10.0
        assert score < 15.0

    def test_clearly_unrelated_colors(self):
        """
        Test 7d: Clearly unrelated colors should score zero.
        """
        score = score_color("blue", "red")
        assert score == 0.0, f"Unrelated colors should score 0, got {score}"

    def test_another_unrelated_pair(self):
        """green and yellow should score zero."""
        score = score_color("green", "yellow")
        assert score == 0.0

    def test_exact_same_color(self):
        """Same color should get full score."""
        score = score_color("black", "black")
        assert score == 15.0

    def test_color_case_insensitive(self):
        """Color matching should be case insensitive."""
        score = score_color("Black", "black")
        assert score == 15.0

    def test_color_with_whitespace(self):
        """Color matching should handle whitespace."""
        score = score_color("  black  ", "black")
        assert score == 15.0

    def test_green_olive_related(self):
        """green and olive should be related."""
        score = score_color("green", "olive")
        assert score >= 10.0
        assert score < 15.0

    def test_white_cream_related(self):
        """white and cream should be related."""
        score = score_color("white", "cream")
        assert score >= 10.0
        assert score < 15.0

    def test_purple_lavender_related(self):
        """purple and lavender should be related."""
        score = score_color("purple", "lavender")
        assert score >= 10.0
        assert score < 15.0


# ============================================================================
# TEST 8: LOCATION MATCHING
# ============================================================================


class TestLocationMatching:
    def test_exact_location(self):
        """
        Test 8a: Exact location match should get full score.
        """
        score = score_location("library", "library")
        assert score == 15.0, f"Exact match should score 15, got {score}"

    def test_same_location_group(self):
        """
        Test 8b: Same location group should get partial score.

        Library and main library are in the same group.
        """
        score = score_location("library", "main library")
        assert score > 0, f"Same group should get partial credit, got {score}"
        assert score < 15, f"Same group should not get full credit, got {score}"

    def test_cafeteria_coffee_shop_related(self):
        """cafeteria and coffee shop are related locations."""
        score = score_location("cafeteria", "coffee shop")
        assert score >= 10.0, f"cafeteria/coffee shop should be related, got {score}"

    def test_unrelated_location(self):
        """
        Test 8c: Unrelated locations should score zero.
        """
        score = score_location("library", "gym")
        assert score == 0.0, f"Unrelated locations should score 0, got {score}"

    def test_another_unrelated_pair(self):
        """engineering building and football field should score zero."""
        score = score_location("engineering building", "football field")
        assert score == 0.0

    def test_location_case_insensitive(self):
        """Location matching should be case insensitive."""
        score = score_location("Library", "library")
        assert score == 15.0

    def test_location_with_whitespace(self):
        """Location matching should handle whitespace."""
        score = score_location("  library  ", "library")
        assert score == 15.0

    def test_library_entrance_related(self):
        """library and library entrance should be related."""
        score = score_location("library", "library entrance")
        assert score >= 7.0, f"library/library entrance should be related, got {score}"

    def test_gym_fitness_center_related(self):
        """gym and fitness center should be related."""
        score = score_location("gym", "fitness center")
        assert score >= 10.0

    def test_dorm_residence_hall_related(self):
        """dorm and residence hall should be related."""
        score = score_location("dorm", "residence hall")
        assert score >= 10.0

    def test_student_center_commons_related(self):
        """student center and commons should be related."""
        score = score_location("student center", "commons")
        assert score >= 10.0

    def test_parking_lot_garage_related(self):
        """parking lot and parking garage should be related."""
        score = score_location("parking lot", "parking garage")
        assert score >= 10.0


# ============================================================================
# ADDITIONAL EDGE CASES
# ============================================================================


class TestEdgeCases:
    def test_empty_descriptions(self):
        """Matching with empty descriptions should still work."""
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
        # Title match should still give some score
        assert result.factor_scores["description"] > 0

    def test_score_never_exceeds_100(self):
        """Score should never exceed 100."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Exact Match",
            description="Exact match description",
            category="electronics",
            color="black",
            location="library",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Exact Match",
            description="Exact match description",
            category="electronics",
            color="black",
            location="library",
            reported_at=datetime(2024, 1, 15, 10, 0, 0),
        )

        result = match_reports(lost, found)
        assert result is not None
        assert result.score <= 100.0

    def test_score_never_negative(self):
        """Score should never be negative."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="A",
            description="B",
            category="electronics",
            color="black",
            location="library",
            reported_at=datetime(2024, 1, 1, 10, 0, 0),
        )
        found = make_report(
            id=2,
            report_type="found",
            title="X",
            description="Y",
            category="accessories",
            color="red",
            location="gym",
            reported_at=datetime(2024, 2, 1, 10, 0, 0),
        )

        result = match_reports(lost, found)
        assert result is not None
        assert result.score >= 0.0

    def test_reasons_are_always_strings(self):
        """All reasons should be non-empty strings."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Blue Book",
            description="Lost blue book",
            category="documents",
            color="blue",
            location="library",
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Blue Book",
            description="Found blue book",
            category="documents",
            color="blue",
            location="library",
        )

        result = match_reports(lost, found)
        assert result is not None
        for reason in result.reasons:
            assert isinstance(reason, str)
            assert len(reason) > 0

    def test_factor_scores_are_within_bounds(self):
        """All factor scores should be within their weight bounds."""
        lost = make_report(
            id=1,
            report_type="lost",
            title="Test",
            description="Test description",
            category="electronics",
            color="black",
            location="library",
        )
        found = make_report(
            id=2,
            report_type="found",
            title="Test",
            description="Test description",
            category="electronics",
            color="black",
            location="library",
        )

        result = match_reports(lost, found)
        assert result is not None

        # Description score should be 0-40
        assert 0 <= result.factor_scores["description"] <= 40
        # Category score should be 0-20
        assert 0 <= result.factor_scores["category"] <= 20
        # Color score should be 0-15
        assert 0 <= result.factor_scores["color"] <= 15
        # Location score should be 0-15
        assert 0 <= result.factor_scores["location"] <= 15
        # Time score should be 0-10
        assert 0 <= result.factor_scores["time"] <= 10

    def test_match_strength_labels(self):
        """Verify correct strength labels for different score ranges."""
        # This test uses the scoring functions directly to verify thresholds
        from app.services.matcher import (
            POSSIBLE_MATCH_MIN,
            STRONG_MATCH_MIN,
            WEAK_MATCH_MIN,
        )

        assert STRONG_MATCH_MIN == 80
        assert POSSIBLE_MATCH_MIN == 60
        assert WEAK_MATCH_MIN == 40
