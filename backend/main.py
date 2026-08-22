import os
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

# CORS configuration — read allowed origins from environment variable.
# Default includes localhost for development; set ALLOWED_ORIGINS in production.
allowed_origins_str = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
)
allowed_origins = [
    origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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


# This block allows running directly with `python main.py` (development)
# or `uvicorn main:app` (production). Render uses the latter.
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
