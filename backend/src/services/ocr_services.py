import io
import logging
import numpy as np
import cv2
from PIL import Image
import easyocr

from ..core.config import settings
from ..utils.image_processor import ImageProcessor

logger = logging.getLogger(__name__)

class OCRService:
    """Service layer for OCR operations"""
    
    def __init__(self):
        self.reader = None
        self.image_processor = ImageProcessor()
        self._initialize_ocr()
    
    def _initialize_ocr(self) -> None:
        """Initialize EasyOCR reader"""
        try:
            self.reader = easyocr.Reader(
                settings.OCR_LANGUAGES,
                gpu=settings.OCR_GPU
            )
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            self.reader = None
    
    def is_healthy(self) -> bool:
        """Check if OCR service is healthy"""
        return self.reader is not None
    
    def validate_image(self, contents: bytes) -> bool:
        """Validate if the uploaded file is a valid image"""
        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()
            return True
        except Exception as e:
            logger.warning(f"Image validation failed: {e}")
            return False
    
    def process_image(self, contents: bytes) -> dict:
        """
        Process image and extract text
        """
        if not self.is_healthy():
            return {
                "success": False,
                "text": "",
                "error": "OCR engine not available"
            }
        
        try:
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(contents))
            
            # Store image metadata
            image_format = pil_image.format
            image_size = f"{pil_image.size[0]}x{pil_image.size[1]}"
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            image_np = np.array(pil_image)
            
            # Preprocess image
            processed_image = self.image_processor.preprocess(image_np)
            
            # Extract text
            result = self._extract_text(processed_image)
            
            # Add image metadata to response
            result.update({
                "image_format": image_format,
                "image_size": image_size
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {
                "success": False,
                "text": "",
                "error": f"Image processing failed: {str(e)}"
            }
    
    def _extract_text(self, image: np.ndarray) -> dict:
        """Extract text from image using EasyOCR"""
        try:
            # Convert image to BGR format for EasyOCR
            if len(image.shape) == 3:
                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            
            # Perform OCR
            results = self.reader.readtext(image_bgr)
            
            # Extract text and confidence scores
            extracted_text = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                extracted_text.append(text)
                confidences.append(confidence)
            
            # Combine all text
            full_text = " ".join(extracted_text)
            
            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "success": True,
                "text": full_text.strip(),
                "confidence": round(avg_confidence, 3),
                "word_count": len(extracted_text),
                "error": None
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                "success": False,
                "text": "",
                "error": f"OCR processing failed: {str(e)}"
            }


ocr_service = OCRService()