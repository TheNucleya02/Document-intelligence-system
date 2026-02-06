import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def preprocess_image(image: Image) -> Image:
    """
    Applies the "Grayscale -> Resize -> Threshold" pipeline to improve OCR accuracy.
    """
    # 1. Convert to Grayscale
    gray_image = image.convert('L')

    # 2. Resize / Rescale
    # Tesseract works best if the text height is at least 30 pixels.
    # We can check the size and scale up if the image is too small.
    # (Note: For PDFs, we handle this via the DPI setting in convert_from_path)
    width, height = gray_image.size
    if width < 1000 or height < 1000:
        scale_factor = 2
        new_size = (width * scale_factor, height * scale_factor)
        gray_image = gray_image.resize(new_size, Image.Resampling.LANCZOS)

    # 3. (Optional) Enhance Contrast / Binarization
    # This makes the text black and background white, removing noise.
    # Simple binary thresholding:
    threshold = 128
    binary_image = gray_image.point(lambda p: 255 if p > threshold else 0)

    return binary_image

def extract_text_from_image(image: Image) -> str:
    """Extracts text from a single PIL Image object using Tesseract."""
    try:
        # Step 1: Preprocess the image (Grayscale, Resize, etc.)
        processed_image = preprocess_image(image)

        # Step 2: Run Tesseract
        # --oem 3: Default engine
        # --psm 6: Assume a single uniform block of text (good for pages)
        # --psm 3: Fully automatic page segmentation (better for mixed layouts)
        custom_config = r'--oem 3 --psm 6' 
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        return text
    except Exception as e:
        logger.warning("Error during OCR extraction", extra={"error": str(e)})
        return ""

def ocr_pdf(file_path: str) -> str:
    """
    Converts a PDF into images (one per page) and performs OCR on each.
    Returns the combined text of the entire document.
    """
    try:
        logger.info("Converting PDF to images at 300 DPI", extra={"path": file_path})
        
        # 1. Convert PDF pages to images
        # Setting dpi=300 satisfies the "Resize" requirement specifically for PDFs
        # This renders the PDF sharply before we even process it.
        images = convert_from_path(file_path, dpi=300)
        
        full_text = []
        for i, image in enumerate(images):
            logger.info("Processing page via OCR", extra={"page": i + 1})
            page_text = extract_text_from_image(image)
            full_text.append(f"--- Page {i+1} ---\n{page_text}")
            
        return "\n".join(full_text)
    except Exception as e:
        logger.warning("Failed to OCR PDF", extra={"path": file_path, "error": str(e)})
        return ""

def ocr_image_file(file_path: str) -> str:
    """Directly processes an image file (JPG, PNG, etc.)."""
    try:
        logger.info("Starting OCR on image", extra={"path": file_path})
        image = Image.open(file_path)
        
        # The preprocessing (Grayscale/Resize) happens inside extract_text_from_image
        text = extract_text_from_image(image)
        
        logger.info("OCR extracted text length", extra={"length": len(text)})
        if not text.strip():
            logger.warning("OCR returned empty text")
            
        return text
    except Exception as e:
        logger.warning("Failed to OCR image", extra={"path": file_path, "error": str(e)})
        return ""
