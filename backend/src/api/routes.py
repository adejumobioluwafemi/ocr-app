from fastapi import APIRouter, File, UploadFile, HTTPException, status
from typing import Dict, Any

from ..core.security import validate_image_content_type, validate_file_size
from ..services.ocr_services import ocr_service
from ..models.schemas import HealthCheck, OCRResponse, ErrorResponse

router = APIRouter()

@router.get("/health", response_model=HealthCheck)
async def health_check() -> HealthCheck:
    """Health check endpoint"""
    return HealthCheck(
        status="healthy" if ocr_service.is_healthy() else "unhealthy",
        ocr_engine="EasyOCR",
        version="1.0.0"
    )

@router.post(
    "/predict", 
    response_model=OCRResponse,
    responses={
        400: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def predict(image: UploadFile = File(...)) -> OCRResponse:
    """
    Process image and extract text using OCR
    
    - **image**: Image file (PNG, JPG, JPEG)
    """
    # Validate file type
    if not validate_image_content_type(image.content_type): # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a supported image type (PNG, JPG, JPEG)"
        )
    
    # Check if OCR service is available
    if not ocr_service.is_healthy():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OCR service temporarily unavailable"
        )
    
    try:
        # Read image contents
        contents = await image.read()
        
        # Validate file size (max 10MB)
        if not validate_file_size(contents, max_size_mb=10):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size too large. Maximum size is 10MB"
            )
        
        # Validate image
        if not ocr_service.validate_image(contents):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
        
        # Process image and extract text
        result = ocr_service.process_image(contents)
        
        return OCRResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "OCR API is running",
        "status": "healthy" if ocr_service.is_healthy() else "unhealthy",
        "version": "1.0.0",
        "docs": "/docs"
    }