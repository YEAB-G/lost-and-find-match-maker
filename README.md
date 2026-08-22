# University Lost & Found Matcher

A full-stack application that automatically identifies potential matches between lost and found item reports using an explainable weighted scoring system.

## 🎯 Project Overview

This application helps university staff identify potential matches between student lost and found reports. Instead of manually reading every report, the system uses a weighted scoring algorithm to surface likely matches with clear explanations.

### Key Features

- **Automated Matching**: Weighted scoring system compares lost and found reports
- **Explainable Results**: Every match includes human-readable reasons
- **Fair Handling**: Missing optional data doesn't penalize matches
- **Clean Interface**: Simple, university-appropriate UI

## 🏗️ Architecture

```
├── backend/           # FastAPI + SQLAlchemy + SQLite
│   ├── app/
│   │   ├── routes/    # API endpoints
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   └── services/  # Business logic
│   └── tests/         # pytest tests
├── frontend/          # React + TypeScript + Vite
│   └── src/           # React components
└── docs/              # Documentation & screenshots
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

The frontend will be available at: http://localhost:5173

### Running Tests

```bash
cd backend
pytest -v
```

## 📊 Matching Algorithm

The system uses a weighted scoring approach:

| Factor | Points | Description |
|--------|--------|-------------|
| Description | 40 | Text similarity using Jaccard index |
| Category | 20 | Item category matching |
| Color | 15 | Color matching with normalization |
| Location | 15 | Location matching with aliases |
| Time | 10 | Temporal proximity |
| **Total** | **100** | |

### Missing Data Handling

When optional fields are missing, the score is normalized against available points:

```
Final Score = (Earned Points / Available Points) × 100
```

This ensures incomplete reports are compared fairly.

## 🧪 Testing

The matching engine is designed to be independently testable:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_matching.py
```

### Test Coverage Focus

- Strong matches between similar reports
- Related locations (e.g., "cafeteria" ↔ "coffee shop")
- Clearly unrelated reports
- Missing optional information handling
- Time proximity scoring
- Color and category normalization

## 🔧 Technical Decisions

### Why Weighted Scoring?

- **Explainable**: Every score can be traced to specific factors
- **Testable**: Each factor can be tested independently
- **Tunable**: Weights can be adjusted based on real usage
- **Simple**: No external AI dependencies required

### Why SQLite?

- Zero configuration required
- Perfect for prototype and development
- Easy to swap to PostgreSQL for production
- Data persists between runs

### Why Manual Aliases?

- Predictable behavior
- Easy to understand and modify
- No external services required
- Can be extended with config files later

## 📝 Design Assumptions

1. **University Context**: Reports come from students describing items in campus locations
2. **English Language**: All reports are in English
3. **Text-Based**: No image processing or OCR in this version
4. **Human-in-the-Loop**: System suggests matches, humans make final decisions
5. **Limited Scope**: Focus on core matching, not authentication or notifications

## ⚠️ Known Limitations

1. **No Semantic Understanding**: Can't match "AirPods" with "wireless earbuds"
2. **Limited Aliases**: Location and color mappings are manually defined
3. **No Learning**: System doesn't improve from user feedback
4. **No Images**: Text-only descriptions (no photo matching)

## 🔮 Future Improvements

With more time, I would add:

- **Word Embeddings**: Better description matching using NLP
- **User Feedback Loop**: Learn from accepted/rejected matches
- **Image Upload**: Photo-based matching with computer vision
- **Notifications**: Email alerts for potential matches
- **Admin Dashboard**: Analytics and reporting
- **Production Database**: PostgreSQL for scalability
- **Authentication**: User accounts and permissions

## 📚 Documentation

- [API Documentation](docs/api.md) - Coming in Phase 3
- [Matching Algorithm](docs/matching.md) - Coming in Phase 2
- [Screenshots](docs/screenshots/) - Coming in Phase 4

## 📄 License

This project is for educational purposes as part of a software engineering assessment.

---

**Phase 1 Complete** ✅
