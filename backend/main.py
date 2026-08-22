from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Report  # noqa: F401
from app.routes import health, matches, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    # Create tables
    Report.metadata.create_all(bind=engine)
    yield
    # Cleanup (if needed)


app = FastAPI(
    title="University Lost & Found Matcher",
    description="Automated matching system for lost and found item reports",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(reports.router)
app.include_router(matches.router)


@app.get("/")
def root():
    return {
        "message": "University Lost & Found Matcher API",
        "docs": "/docs",
        "health": "/health",
    }
