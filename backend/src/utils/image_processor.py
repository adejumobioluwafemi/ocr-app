import logging
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Utility class for image processing operations"""
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Basic image preprocessing for better OCR results
        """
        try:
            # Convert to grayscale if it's a color image
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Apply simple denoising
            denoised = cv2.medianBlur(gray, 3)
            
            return denoised
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE"""
        try:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(image)
            return enhanced
        except Exception as e:
            logger.warning(f"Contrast enhancement failed: {e}")
            return image