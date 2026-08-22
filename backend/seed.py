"""
Seed data for the University Lost & Found Matcher.

Creates realistic sample reports that demonstrate the matching system.

Usage:
    python seed.py          # Seed the database
    python seed.py --reset  # Clear all data and reseed

The script is idempotent when run without --reset.
"""

import sys
from datetime import datetime

from app.database import Base, SessionLocal, engine
from app.models import Report


# ============================================================================
# SEED DATA
# ============================================================================

LOST_REPORTS = [
    {
        "report_type": "lost",
        "title": "Black AirPods Case",
        "description": "Lost black AirPods case in the cafeteria. Has a small scratch on the front.",
        "category": "electronics",
        "color": "black",
        "location": "cafeteria",
        "reported_at": datetime(2024, 1, 15, 14, 30, 0),
    },
    {
        "report_type": "lost",
        "title": "Blue Dell Laptop",
        "description": "Left my blue Dell laptop in the engineering building study room. It was in a gray sleeve.",
        "category": "electronics",
        "color": None,  # Missing color - student wasn't sure
        "location": "engineering building",
        "reported_at": datetime(2024, 1, 14, 16, 0, 0),
    },
    {
        "report_type": "lost",
        "title": "Black Jansport Backpack",
        "description": "Lost black backpack near the library. Has textbooks and a water bottle.",
        "category": "bags",
        "color": "black",
        "location": "library",
        "reported_at": datetime(2024, 1, 15, 10, 0, 0),
    },
    {
        "report_type": "lost",
        "title": "Red Leather Wallet",
        "description": "Lost leather wallet near the cafeteria. Red color with student ID inside.",
        "category": "accessories",
        "color": "red",
        "location": "cafeteria",
        "reported_at": datetime(2024, 1, 15, 12, 0, 0),
    },
    {
        "report_type": "lost",
        "title": "Car Keys with Keychain",
        "description": "Lost car keys in the parking lot. Has a university keychain.",
        "category": None,  # Missing category - student wasn't sure how to categorize
        "color": "silver",
        "location": "parking lot",
        "reported_at": datetime(2024, 1, 12, 8, 30, 0),
    },
]

FOUND_REPORTS = [
    {
        "report_type": "found",
        "title": "Black AirPods Case",
        "description": "Found black AirPods case near the cafeteria. Looks recently lost.",
        "category": "electronics",
        "color": "black",
        "location": "cafeteria",
        "reported_at": datetime(2024, 1, 15, 16, 0, 0),
    },
    {
        "report_type": "found",
        "title": "Blue Spiral Notebook",
        "description": "Found a blue spiral notebook on a library table. Has some handwritten notes inside.",
        "category": "documents",
        "color": "blue",
        "location": "library",
        "reported_at": datetime(2024, 1, 16, 9, 0, 0),
    },
    {
        "report_type": "found",
        "title": "Black Backpack",
        "description": "Found black backpack at the library. Contains textbooks and a water bottle.",
        "category": "bags",
        "color": "black",
        "location": "library",
        "reported_at": datetime(2024, 1, 16, 11, 0, 0),
    },
    {
        "report_type": "found",
        "title": "Blue Wallet",
        "description": "Found leather wallet in the cafeteria. Blue color, appears to be recently lost.",
        "category": "accessories",
        "color": "blue",
        "location": "cafeteria",
        "reported_at": datetime(2024, 1, 15, 18, 0, 0),
    },
    {
        "report_type": "found",
        "title": "Set of Car Keys",
        "description": "Found car keys in the parking garage. Has a university keychain.",
        "category": None,  # Missing category
        "color": "metallic",
        "location": "parking lot",
        "reported_at": datetime(2024, 1, 12, 14, 0, 0),
    },
]


# ============================================================================
# SEED FUNCTION
# ============================================================================


def seed_database(reset: bool = False):
    """Seed the database with sample reports."""
    db = SessionLocal()

    try:
        if reset:
            print("Clearing existing reports...")
            db.query(Report).delete()
            db.commit()
            print("Database cleared.")

        # Check if data already exists
        existing_count = db.query(Report).count()
        if existing_count > 0 and not reset:
            print(f"Database already has {existing_count} reports.")
            print("Use --reset to clear and reseed.")
            return

        print("Seeding lost reports...")
        for data in LOST_REPORTS:
            report = Report(**data)
            db.add(report)

        print("Seeding found reports...")
        for data in FOUND_REPORTS:
            report = Report(**data)
            db.add(report)

        db.commit()
        print(f"Successfully seeded {len(LOST_REPORTS)} lost and {len(FOUND_REPORTS)} found reports.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    reset = "--reset" in sys.argv
    seed_database(reset=reset)
