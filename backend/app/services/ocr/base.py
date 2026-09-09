from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class OCRToken(BaseModel):
    text: str
    confidence: float
    box: Dict[str, float]  # {"x": 0-100, "y": 0-100, "w": 0-100, "h": 0-100, "page": 1}


class OCRResult(BaseModel):
    raw_text: str
    provider_name: str
    tokens: List[OCRToken]
    metadata: Optional[Dict[str, Any]] = None


class BaseOCRProvider(ABC):
    @abstractmethod
    async def extract_text_and_boxes(self, file_path: str, file_bytes: bytes) -> OCRResult:
        """Extract raw text, word tokens, bounding boxes, and confidence levels."""
        pass
