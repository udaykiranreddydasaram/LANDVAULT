from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.core.config import settings
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.models import *  # Ensure all models are registered
from backend.app.api.v1.api import api_router
from backend.app.demo.seed_data import seed_database_if_empty


# Ensure tables exist immediately
Base.metadata.create_all(bind=engine)
_db_init = SessionLocal()
try:
    seed_database_if_empty(_db_init)
finally:
    _db_init.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Keep database tables synced
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"{settings.PROJECT_TAGLINE} - Smart India Hackathon Prototype (SIH26018)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories for uploaded deeds and sample images
app.mount("/storage/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")
app.mount("/samples", StaticFiles(directory=str(settings.SAMPLES_DIR)), name="samples")

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "tagline": settings.PROJECT_TAGLINE,
        "status": "ONLINE",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
