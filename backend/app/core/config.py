import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
PROCESSED_DIR = STORAGE_DIR / "processed"
SAMPLES_DIR = BASE_DIR / "samples"

for d in [STORAGE_DIR, UPLOADS_DIR, PROCESSED_DIR, SAMPLES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    PROJECT_NAME: str = "LANDVAULT AI"
    PROJECT_TAGLINE: str = "From Legacy Records to Trusted Digital Land Data"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "landvault-ai-secret-key-for-smart-india-hackathon-2026-super-secure")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for hackathon ease
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/landvault.db")
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    STORAGE_DIR: Path = STORAGE_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    PROCESSED_DIR: Path = PROCESSED_DIR
    SAMPLES_DIR: Path = SAMPLES_DIR

    # OCR and Confidence Config
    CONFIDENCE_HIGH_THRESHOLD: float = 0.90
    CONFIDENCE_MEDIUM_THRESHOLD: float = 0.70
    DEFAULT_OCR_PROVIDER: str = "mock"  # "mock" or "tesseract"


settings = Settings()
