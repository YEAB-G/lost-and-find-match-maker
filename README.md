# University Lost & Found Matcher

A full-stack application that automatically identifies potential matches between lost and found item reports on a university campus, using an explainable weighted scoring system.

---

## 1. Project Overview

On a typical university campus, students lose items daily and good Samaritans find them just as often. Staff manually read through reports to find potential matches — a slow, error-prone process that delays getting items back to their owners.

This application solves that problem by accepting lost and found reports, then using a weighted scoring algorithm to automatically surface likely matches with clear, human-readable explanations.

---

## 2. Features

- **Create Reports** — Submit lost or found item reports with title, description, location, date/time, and optional category/color fields.
- **Browse and Filter** — View all reports with filtering by type (lost, found, or all).
- **Automated Matching** — Select any report to find ranked potential matches from opposite-type reports.
- **Explainable Scores** — Every match shows a percentage score, strength label (strong/possible/weak), and specific reasons why it matched.
- **Score Breakdown** — Expandable detail showing individual factor scores (description, category, color, location, time).
- **Missing Data Handling** — Missing optional fields (category, color) are excluded from scoring, not treated as mismatches.
- **Mobile-Responsive UI** — Dark-themed interface that adapts to different screen sizes.

---

## 3. Approach

The system follows a **deterministic, explainable** matching approach:

1. A user submits a lost or found report via the frontend form.
2. Reports are stored in an SQLite database via the FastAPI backend.
3. When a user clicks "Find Matches" on any report, the backend retrieves all reports of the opposite type.
4. Each candidate is compared using a weighted scoring engine that evaluates five factors.
5. Matches below a minimum threshold are filtered out.
6. Remaining matches are sorted by score (highest first) and returned with reasons.

No machine learning, external APIs, or probabilistic models are used. Every score is fully traceable to its component factors.

---

## 4. Matching System

### 4.1 Factor Weights

| Factor | Max Points | Weight | Description |
|--------|-----------|--------|-------------|
| Description | 40 | 40% | Text similarity between title + description |
| Category | 20 | 20% | Item category matching (optional) |
| Color | 15 | 15% | Color matching with normalization (optional) |
| Location | 15 | 15% | Location matching with alias support |
| Time | 10 | 10% | Temporal proximity of reports |
| **Total** | **100** | | |

### 4.2 Description Matching

Combines two similarity measures:
- **Jaccard token similarity** (60% weight) — measures word overlap between normalized texts.
- **Sequence similarity** (40% weight) — uses Python's `SequenceMatcher` for phrase-level similarity.

Both title and description are concatenated for comparison. Text is lowercased, punctuation removed, and whitespace normalized before comparison.

### 4.3 Category Matching

- Exact match: full score (20 points).
- Any mismatch: 0 points.
- Missing from either report: factor excluded from scoring (see normalization).

### 4.4 Color Matching

- **Exact match** (e.g., "black" = "black"): full score (15 points).
- **Related colors** (e.g., "black" and "dark", "blue" and "navy"): 70% score (10.5 points).
- **Unrelated colors** (e.g., "blue" and "red"): 0 points.
- **Equivalents** (e.g., "grey" = "gray"): treated as exact match.
- Missing from either report: factor excluded.

Related colors are organized into groups: black/dark/charcoal/midnight, blue/navy/cobalt/azure, red/maroon/crimson/burgundy, green/olive/emerald/forest, white/cream/ivory/pearl, brown/tan/beige/khaki, pink/rose/salmon/magenta, yellow/gold/amber, purple/violet/lavender/plum, orange/coral/peach.

### 4.5 Location Matching

- **Exact match**: full score (15 points).
- **Same location group** (e.g., "cafeteria" and "coffee shop"): 70% score (10.5 points).
- **Substring match** (e.g., "library" within "main library"): 50% score (7.5 points).
- **No match**: 0 points.

Location groups: library variants, cafeteria/coffee shop/canteen/dining hall/cafe, gym/fitness center/sports center/recreation center, dorm/dormitory/residence hall/student housing, student center/student union/commons, parking lot/parking garage/parking structure, admin building/administration/admin office.

### 4.6 Time Proximity

- **Same calendar day**: full score (10 points).
- **Within 24 hours (different days)**: 80% score (8 points).
- **Within 3 days**: 50% score (5 points).
- **Within 7 days**: 20% score (2 points).
- **More than 7 days**: 0 points.

### 4.7 Missing Data Normalization

When optional fields (category, color) are missing from either report, that factor is excluded from both earned and available points:

```
Final Score = (Earned Points / Available Points) × 100
```

This ensures a report with missing color is not penalized — it is compared only on the factors that are available.

### 4.8 Match Thresholds

| Strength | Minimum Score | Display |
|----------|--------------|---------|
| Strong | 80% | Green badge |
| Possible | 60% | Yellow badge |
| Weak | 40% | Orange badge |
| Below threshold | < 40% | Filtered out |

### 4.9 Explainable Reasons

Every match includes human-readable reasons drawn from the scoring factors:
- "Strong item description similarity"
- "Matching category: electronics"
- "Matching color: black"
- "Similar colors: blue and navy"
- "Matching location: library"
- "Related locations"
- "Reports made on the same day"
- "Reports were made within one day"

---

## 5. Important Assumptions

1. **University context** — Reports come from students describing items in campus locations.
2. **English language** — All reports are in English; no internationalization.
3. **Text-based** — No image processing, OCR, or photo matching.
4. **Human-in-the-loop** — The system suggests matches; humans make final decisions.
5. **No user accounts** — Reports are anonymous; no authentication.
6. **Single-campus** — No multi-campus or cross-institution matching.

---

## 6. Technical Decisions

### Why Python/FastAPI for the backend?
- FastAPI provides automatic request validation via Pydantic schemas.
- SQLAlchemy provides a clean ORM layer over SQLite.
- Simple to set up with no external infrastructure dependencies.

### Why React/TypeScript for the frontend?
- TypeScript provides type safety across API calls and component props.
- React's component model fits the distinct views (form, list, matches).
- Vite provides fast development and build times.

### Why SQLite?
- Zero configuration required — no database server to install.
- Data persists between runs.
- Easy to swap to PostgreSQL for production.
- Sufficient for the application's scale.

### Why weighted scoring instead of ML?
- Fully explainable — every score can be traced to specific factors.
- Independently testable — each factor can be verified in isolation.
- Tunable — weights can be adjusted based on real usage data.
- No training data or external dependencies required.
- Predictable behavior that is easy to debug.

### Why manual aliases for colors/locations?
- Predictable, testable behavior.
- Easy to understand and modify.
- No external services or NLP libraries required.

---

## 7. Project Structure

```
lost-found-matcher/
├── backend/
│   ├── app/
│   │   ├── models/         # SQLAlchemy ORM models
│   │   │   └── report.py   # Report database model
│   │   ├── routes/         # FastAPI endpoint handlers
│   │   │   ├── reports.py  # CRUD for reports
│   │   │   ├── matches.py  # Match finding endpoint
│   │   │   └── health.py   # Health check
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   │   ├── report.py   # Report schemas
│   │   │   └── match.py    # Match response schemas
│   │   ├── services/       # Business logic
│   │   │   └── matcher.py  # Weighted scoring engine
│   │   └── database.py     # SQLAlchemy engine and session
│   ├── tests/              # pytest test suite (90 tests)
│   ├── main.py             # FastAPI app entry point
│   ├── seed.py             # Sample data seeder
│   └── requirements.txt    # Python dependencies
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ReportForm.tsx   # Report creation form
│       │   ├── ReportList.tsx   # Report listing with filters
│       │   ├── MatchResults.tsx # Match results view
│       │   └── MatchCard.tsx    # Individual match display
│       ├── api.ts          # API client and type definitions
│       ├── App.tsx         # Root component with routing
│       └── index.css       # Global styles
├── docs/
│   └── screenshots/        # Application screenshots
└── README.md
```

---

## 8. How to Run

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API is available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend is available at `http://localhost:5173`.

### Database Setup

The SQLite database is created automatically on first backend startup. No manual setup required.

To reset the database, delete `backend/lost_found.db` and restart the backend.

### Seed Data

```bash
cd backend
source venv/bin/activate

# Seed with sample reports (idempotent — safe to run multiple times)
python seed.py

# Clear and reseed
python seed.py --reset
```

### Running Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_matcher.py
```

---

## 9. API Overview

| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| GET | `/` | API info | 200 |
| GET | `/health` | Health check | 200 |
| POST | `/reports` | Create a report | 201 |
| GET | `/reports` | List reports (optional `?type=lost\|found`) | 200 |
| GET | `/reports/{id}` | Get single report | 200 |
| GET | `/reports/{id}/matches` | Find matches for a report | 200 |

### POST /reports

Request body:
```json
{
  "report_type": "lost",
  "title": "Black AirPods Case",
  "description": "Lost my AirPods near the cafeteria",
  "category": "electronics",
  "color": "black",
  "location": "cafeteria",
  "reported_at": "2024-01-15T10:30:00"
}
```

Required fields: `report_type`, `title`, `description`, `location`, `reported_at`.
Optional fields: `category`, `color`.

### GET /reports/{id}/matches

Response:
```json
{
  "report": { ... },
  "matches": [
    {
      "matched_report": { ... },
      "score": 85.5,
      "strength": "strong",
      "reasons": [
        "Strong item description similarity",
        "Matching category: electronics",
        "Matching color: black",
        "Matching location: cafeteria",
        "Reports made on the same day"
      ],
      "factor_scores": {
        "description": 35.2,
        "category": 20.0,
        "color": 15.0,
        "location": 15.0,
        "time": 10.0
      }
    }
  ],
  "total_candidates": 3,
  "qualifying_matches": 1
}
```

---

## 10. Tests

The test suite contains **90 tests** across 5 test files:

| File | Tests | Covers |
|------|-------|--------|
| `test_matcher.py` | 57 | Scoring engine: each factor, missing data, edge cases |
| `test_matches.py` | 14 | Match endpoint: sorting, filtering, 404 handling |
| `test_reports.py` | 17 | Report CRUD: creation, validation, listing, filtering |
| `test_health.py` | 2 | Health check and root endpoints |

### Key behaviors verified:

- **Strong matches** between similar lost/found reports.
- **Related items** (e.g., "backpack" descriptions with different wording).
- **Clearly unrelated** reports score below threshold.
- **Missing optional data** is normalized, not penalized.
- **Same report type** comparisons are rejected.
- **Time proximity** scoring at day, 3-day, and 7-day boundaries.
- **Color normalization** — grey/gray equivalence, related color groups.
- **Location aliases** — cafeteria/coffee shop, gym/fitness center.
- **Sorting** — matches returned highest score first.
- **404 handling** — missing report IDs return proper errors.
- **Validation** — empty fields, future dates, invalid types rejected.

---

## 11. What I Intentionally Did Not Build

These features were excluded to maintain focus on the core matching problem:

- **Authentication / User accounts** — No login system; reports are anonymous.
- **Notifications** — No email, push, or in-app alerts for potential matches.
- **Image uploads** — No photo support for items.
- **OCR** — No text extraction from images.
- **Advanced semantic matching** — No NLP, word embeddings, or transformer models to match "AirPods" with "wireless earbuds."
- **Production deployment** — No Docker, CI/CD, or cloud hosting setup.
- **Duplicate report detection** — No deduplication of similar reports.

---

## 12. What I Would Improve with More Time

Realistic improvements in priority order:

1. **Semantic matching** — Use word embeddings or a small language model to match descriptions that use different words for the same item (e.g., "AirPods" ↔ "wireless earbuds").
2. **More location intelligence** — Fuzzy location matching using building names, building numbers, or campus map coordinates.
3. **Image support** — Allow photo uploads for visual matching and better report identification.
4. **Duplicate detection** — Automatically detect and flag when users submit very similar reports.
5. **Human review workflow** — Let staff confirm or reject suggested matches, feeding back into the system.
6. **Match feedback loop** — Collect data on which matches were accepted to improve scoring weights over time.
7. **User accounts** — Let students track their reports and check for updates.
8. **Notifications** — Email or push alerts when a potential match is found.
9. **Production database** — Migrate to PostgreSQL for scalability.
10. **Deployment** — Docker containerization and cloud hosting.

---

## 13. Screenshots

> **TODO**: Add actual screenshots of the application.
>
> Screenshot locations to capture:
>
> 1. `docs/screenshots/main-page.png` — Main page showing the status banner, report form, and report list with filter buttons.
> 2. `docs/screenshots/report-form.png` — The report creation form with type toggle, required fields, and optional details section.
> 3. `docs/screenshots/match-results.png` — Match results view showing the selected report, match summary, and ranked match cards with scores and reasons.
>
> To take screenshots: start both the backend (`uvicorn main:app --reload --port 8000`) and frontend (`npm run dev`), then capture the screens above.

---

## 14. AI Usage

I used Codex as an AI coding assistant during development, mainly to speed up implementation and handle routine coding tasks.

### My Role

I was responsible for the main engineering decisions throughout the project. This included:

- Understanding the requirements and defining the solution.
- Deciding the system architecture and project structure.
- Breaking the work into implementation phases.
- Choosing the matching approach and scoring logic.
- Deciding which report attributes should affect a match.
- Defining how missing data should be handled.
- Reviewing generated code and deciding whether it met the requirements.
- Testing the application and validating the results.
- Identifying issues and deciding how they should be fixed.

### How I Used AI

I used Codex as an AI coding assistant for implementation support, including:

- Generating boilerplate and repetitive code.
- Implementing components based on requirements I defined.
- Helping with routine backend and frontend code.
- Assisting with dependency updates and compatibility fixes.
- Helping debug errors after I identified and provided the issue.
- Generating test cases based on scenarios I requested.
- Reviewing code for obvious errors or duplication.
- Assisting with documentation and deployment preparation.

I worked iteratively rather than asking AI to build the project without direction. I first defined the task or problem, then used Codex to help implement or investigate it. I reviewed the output, tested it locally, and refined the implementation where needed.

### Development Approach

The workflow was:

1. I analyzed the project requirements.
2. I decided the architecture and core implementation approach.
3. I broke the project into smaller development phases.
4. I defined the requirements for each phase.
5. Codex assisted with implementing the requested code.
6. I reviewed the implementation and tested it.
7. I identified issues and guided further changes.
8. I made the final decisions about what remained in the project.

AI was used to increase development speed, not to replace engineering judgment. The core design decisions, requirements, review process, and validation remained my responsibility.
