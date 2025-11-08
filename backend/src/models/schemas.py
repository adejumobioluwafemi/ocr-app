from pydantic import BaseModel
from typing import Optional

class HealthCheck(BaseModel):
    status: Optional[str] = None
    ocr_engine: Optional[str] = None
    version: Optional[str] = None

class OCRRequest(BaseModel):
    image_format: Optional[str] = None
    image_size: Optional[str] = None

class OCRResponse(BaseModel):
    success: bool
    text: str
    confidence: Optional[float] = None
    word_count: Optional[int] = None
    error: Optional[str] = None
    image_format: Optional[str] = None
    image_size: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None