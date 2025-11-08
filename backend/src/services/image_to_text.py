import io
from PIL import Image
from fastapi import HTTPException, File, UploadFile
import numpy as np
from main import reader
from backend.src.utils.image_processor import ocr_processor
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def predict(image: UploadFile = File(...)):
    """
    easyocr endpoint - process image and extract text
    """

    if not image.content_type.startswith('image/'): # type: ignore
        raise HTTPException(
            status_code=400,
            detail = "File must be an image (PNG, JPG, JPEG)"
        )
    
    if reader is None:
        raise HTTPException(
            status_code=503,
            detail="EasyOCR service temporarily unavailable"
        )
    
    try:
        contents = await image.read()

        if not ocr_processor.validate_image(contents): # type: ignore
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )
        
        pil_image = Image.open(io.BytesIO(contents))

        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        image_np = np.array(pil_image)
        processed_image = ocr_processor.process_image(image_np)

        result = ocr_processor.extract_text(processed_image)

        result.update({
            "image_format": pil_image.format,
            "image_size": f"{pil_image.size[0]}x{pil_image.size[1]}"
        })

        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
            
        