from fastapi import HTTPException, status
from typing import List

def validate_image_content_type(content_type: str) -> bool:
    """Validate if the file is a supported image type"""
    supported_types = ["image/png", "image/jpeg", "image/jpg"]
    return content_type in supported_types

def validate_file_size(content: bytes, max_size_mb: int = 10) -> bool:
    """Validate file size"""
    max_size = max_size_mb * 1024 * 1024  # Convert to bytes
    return len(content) <= max_size