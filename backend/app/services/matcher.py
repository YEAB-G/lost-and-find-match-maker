"""
Matching Engine for University Lost & Found Matcher.

This module provides deterministic, explainable matching between lost and found reports.
It uses weighted scoring across multiple factors and handles missing data gracefully.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Optional

# ============================================================================
# CONSTANTS - Weights and Thresholds
# ============================================================================

# Factor weights (total: 100)
DESCRIPTION_WEIGHT = 40
CATEGORY_WEIGHT = 20
COLOR_WEIGHT = 15
LOCATION_WEIGHT = 15
TIME_WEIGHT = 10

# Match strength thresholds
STRONG_MATCH_MIN = 80
POSSIBLE_MATCH_MIN = 60
WEAK_MATCH_MIN = 40

# Time proximity thresholds (in days)
TIME_SAME_DAY = 0
TIME_WITHIN_1_DAY = 1
TIME_WITHIN_3_DAYS = 3
TIME_WITHIN_7_DAYS = 7

# ============================================================================
# COLOR NORMALIZATION
# ============================================================================

# Colors that are considered equivalent
COLOR_EQUIVALENTS = {
    "grey": "gray",
    "gray": "gray",
}

# Color groups - colors within same group are considered related
COLOR_GROUPS = [
    {"black", "dark", "charcoal", "midnight"},
    {"blue", "navy", "cobalt", "azure"},
    {"red", "maroon", "crimson", "burgundy"},
    {"green", "olive", "emerald", "forest"},
    {"white", "cream", "ivory", "pearl"},
    {"brown", "tan", "beige", "khaki"},
    {"pink", "rose", "salmon", "magenta"},
    {"yellow", "gold", "amber"},
    {"purple", "violet", "lavender", "plum"},
    {"orange", "coral", "peach"},
]

# ============================================================================
# LOCATION ALIASES
# ============================================================================

# Location groups - locations within same group are considered related
LOCATION_GROUPS = [
    {"library", "main library", "library entrance", "study hall"},
    {"cafeteria", "coffee shop", "canteen", "dining hall", "cafe"},
    {"gym", "fitness center", "sports center", "recreation center"},
    {"dorm", "dormitory", "residence hall", "student housing"},
    {"student center", "student union", "commons"},
    {"parking lot", "parking garage", "parking structure"},
    {"admin building", "administration", "admin office"},
]

# ============================================================================
# VALID CATEGORIES
# ============================================================================

VALID_CATEGORIES = {
    "electronics",
    "bags",
    "clothing",
    "keys",
    "documents",
    "accessories",
    "other",
}

# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class Report:
    """Simple report data class for matching."""

    id: int
    report_type: str  # "lost" or "found"
    title: str
    description: str
    category: Optional[str]
    color: Optional[str]
    location: str
    reported_at: datetime
    created_at: datetime


@dataclass
class MatchResult:
    """Result of comparing two reports."""

    score: float  # Normalized score 0-100
    strength: str  # "strong", "possible", "weak", "below_threshold"
    reasons: list[str] = field(default_factory=list)
    factor_scores: dict[str, Optional[float]] = field(default_factory=dict)
    factor_available: dict[str, bool] = field(default_factory=dict)
    earned_points: float = 0
    available_points: float = 0


# ============================================================================
# TEXT PROCESSING HELPERS
# ============================================================================


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Remove punctuation (keep spaces and alphanumeric)
    text = re.sub(r"[^\w\s]", " ", text)

    # Collapse multiple whitespace
    text = re.sub(r"\s+", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def extract_tokens(text: str) -> set[str]:
    """Extract meaningful tokens from text."""
    normalized = normalize_text(text)
    if not normalized:
        return set()

    # Split into words and filter out very short tokens
    tokens = set(normalized.split())
    tokens = {t for t in tokens if len(t) > 1}
    return tokens


def calculate_token_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts using token overlap."""
    tokens1 = extract_tokens(text1)
    tokens2 = extract_tokens(text2)

    if not tokens1 and not tokens2:
        return 0.0

    if not tokens1 or not tokens2:
        return 0.0

    # Jaccard similarity
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2

    if not union:
        return 0.0

    return len(intersection) / len(union)


def calculate_sequence_similarity(text1: str, text2: str) -> float:
    """Calculate sequence similarity using SequenceMatcher."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)

    if not norm1 or not norm2:
        return 0.0

    return SequenceMatcher(None, norm1, norm2).ratio()


# ============================================================================
# FACTOR SCORING FUNCTIONS
# ============================================================================


def score_description(title1: str, desc1: str, title2: str, desc2: str) -> float:
    """
    Score description similarity between two reports.

    Combines token overlap and sequence similarity for robust matching.
    Returns score between 0 and DESCRIPTION_WEIGHT (40).
    """
    # Combine title and description for each report
    combined1 = f"{title1} {desc1}"
    combined2 = f"{title2} {desc2}"

    # Calculate both similarity measures
    token_sim = calculate_token_similarity(combined1, combined2)
    seq_sim = calculate_sequence_similarity(combined1, combined2)

    # Weighted combination: token similarity is more important for keyword matching
    # sequence similarity helps with similar phrasing
    combined_sim = (token_sim * 0.6) + (seq_sim * 0.4)

    return combined_sim * DESCRIPTION_WEIGHT


def score_category(cat1: Optional[str], cat2: Optional[str]) -> Optional[float]:
    """
    Score category similarity.

    Returns None if either category is missing (factor unavailable).
    Returns score between 0 and CATEGORY_WEIGHT (20).
    """
    # Missing data handling - exclude factor
    if not cat1 or not cat2:
        return None

    cat1 = cat1.lower().strip()
    cat2 = cat2.lower().strip()

    # Exact match
    if cat1 == cat2:
        return CATEGORY_WEIGHT

    # No match
    return 0.0


def score_color(color1: Optional[str], color2: Optional[str]) -> Optional[float]:
    """
    Score color similarity with normalization.

    Returns None if either color is missing (factor unavailable).
    Returns score between 0 and COLOR_WEIGHT (15).
    """
    # Missing data handling - exclude factor
    if not color1 or not color2:
        return None

    color1 = color1.lower().strip()
    color2 = color2.lower().strip()

    # Normalize equivalent colors
    color1 = COLOR_EQUIVALENTS.get(color1, color1)
    color2 = COLOR_EQUIVALENTS.get(color2, color2)

    # Exact match
    if color1 == color2:
        return COLOR_WEIGHT

    # Check if colors are in the same group (related)
    for group in COLOR_GROUPS:
        if color1 in group and color2 in group:
            return COLOR_WEIGHT * 0.7  # 70% for related colors

    # No match
    return 0.0


def score_location(loc1: str, loc2: str) -> float:
    """
    Score location similarity with alias support.

    Returns score between 0 and LOCATION_WEIGHT (15).
    """
    loc1 = loc1.lower().strip()
    loc2 = loc2.lower().strip()

    # Exact match
    if loc1 == loc2:
        return LOCATION_WEIGHT

    # Check if locations are in the same group (related)
    for group in LOCATION_GROUPS:
        if loc1 in group and loc2 in group:
            return LOCATION_WEIGHT * 0.7  # 70% for related locations

    # Check for substring matches (e.g., "library" in "main library")
    if loc1 in loc2 or loc2 in loc1:
        return LOCATION_WEIGHT * 0.5  # 50% for substring matches

    # No match
    return 0.0


def score_time(dt1: datetime, dt2: datetime) -> float:
    """
    Score time proximity.

    Returns score between 0 and TIME_WEIGHT (10).
    """
    # Calculate time difference
    diff = abs(dt1 - dt2)
    days_diff = diff.total_seconds() / (24 * 3600)

    # Check if same calendar day
    same_day = dt1.date() == dt2.date()

    # Same day (same calendar date)
    if same_day:
        return TIME_WEIGHT

    # Within 1 day (less than 24 hours apart, different days)
    if days_diff <= TIME_WITHIN_1_DAY:
        return TIME_WEIGHT * 0.8

    # Within 3 days
    if days_diff <= TIME_WITHIN_3_DAYS:
        return TIME_WEIGHT * 0.5

    # Within 7 days
    if days_diff <= TIME_WITHIN_7_DAYS:
        return TIME_WEIGHT * 0.2

    # More than 7 days
    return 0.0


# ============================================================================
# REASON GENERATION
# ============================================================================


def generate_reasons(
    description_score: float,
    category_score: Optional[float],
    color_score: Optional[float],
    location_score: float,
    time_score: float,
    cat1: Optional[str],
    cat2: Optional[str],
    color1: Optional[str],
    color2: Optional[str],
    loc1: str,
    loc2: str,
    days_diff: float,
) -> list[str]:
    """Generate human-readable reasons for the match."""
    reasons = []

    # Description reasons
    if description_score >= DESCRIPTION_WEIGHT * 0.7:
        reasons.append("Strong item description similarity")
    elif description_score >= DESCRIPTION_WEIGHT * 0.4:
        reasons.append("Moderate item description similarity")

    # Category reasons
    if category_score is not None:
        if category_score == CATEGORY_WEIGHT:
            reasons.append(f"Matching category: {cat1}")
        elif category_score > 0:
            reasons.append("Related category")

    # Color reasons
    if color_score is not None:
        if color_score == COLOR_WEIGHT:
            reasons.append(f"Matching color: {color1}")
        elif color_score > 0:
            reasons.append(f"Similar colors: {color1} and {color2}")

    # Location reasons
    if location_score >= LOCATION_WEIGHT * 0.7:
        if loc1 == loc2:
            reasons.append(f"Matching location: {loc1}")
        else:
            reasons.append("Related locations")
    elif location_score >= LOCATION_WEIGHT * 0.4:
        reasons.append("Nearby locations")

    # Time reasons
    if time_score >= TIME_WEIGHT * 0.8:
        reasons.append("Reports made on the same day")
    elif time_score >= TIME_WEIGHT * 0.5:
        reasons.append("Reports were made within one day")
    elif time_score >= TIME_WEIGHT * 0.2:
        reasons.append("Reports were made within a few days")

    return reasons


# ============================================================================
# MAIN MATCHING FUNCTION
# ============================================================================


def match_reports(report1: Report, report2: Report) -> Optional[MatchResult]:
    """
    Compare two reports and return a match result.

    Args:
        report1: First report (can be lost or found)
        report2: Second report (must be opposite type)

    Returns:
        MatchResult if comparison is valid, None if reports are same type
    """
    # Validate report types are different
    if report1.report_type == report2.report_type:
        return None

    # Ensure report1 is lost and report2 is found for consistency
    if report1.report_type == "found":
        report1, report2 = report2, report1

    # Calculate factor scores
    desc_score = score_description(
        report1.title, report1.description,
        report2.title, report2.description
    )

    cat_score = score_category(report1.category, report2.category)
    color_score = score_color(report1.color, report2.color)
    loc_score = score_location(report1.location, report2.location)
    time_score = score_time(report1.reported_at, report2.reported_at)

    # Calculate available points
    available_points = DESCRIPTION_WEIGHT + LOCATION_WEIGHT + TIME_WEIGHT
    if cat_score is not None:
        available_points += CATEGORY_WEIGHT
    if color_score is not None:
        available_points += COLOR_WEIGHT

    # Calculate earned points
    earned_points = desc_score + loc_score + time_score
    if cat_score is not None:
        earned_points += cat_score
    if color_score is not None:
        earned_points += color_score

    # Normalize score
    if available_points > 0:
        normalized_score = (earned_points / available_points) * 100
    else:
        normalized_score = 0.0

    # Round to 1 decimal
    normalized_score = round(normalized_score, 1)

    # Determine match strength
    if normalized_score >= STRONG_MATCH_MIN:
        strength = "strong"
    elif normalized_score >= POSSIBLE_MATCH_MIN:
        strength = "possible"
    elif normalized_score >= WEAK_MATCH_MIN:
        strength = "weak"
    else:
        strength = "below_threshold"

    # Generate reasons
    days_diff = abs(report1.reported_at - report2.reported_at).total_seconds() / (24 * 3600)
    reasons = generate_reasons(
        desc_score, cat_score, color_score, loc_score, time_score,
        report1.category, report2.category,
        report1.color, report2.color,
        report1.location, report2.location,
        days_diff,
    )

    return MatchResult(
        score=normalized_score,
        strength=strength,
        reasons=reasons,
        factor_scores={
            "description": round(desc_score, 2),
            "category": round(cat_score, 2) if cat_score is not None else None,
            "color": round(color_score, 2) if color_score is not None else None,
            "location": round(loc_score, 2),
            "time": round(time_score, 2),
        },
        factor_available={
            "description": True,
            "category": cat_score is not None,
            "color": color_score is not None,
            "location": True,
            "time": True,
        },
        earned_points=round(earned_points, 2),
        available_points=available_points,
    )
