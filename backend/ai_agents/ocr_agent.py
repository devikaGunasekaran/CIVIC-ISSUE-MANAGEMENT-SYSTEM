"""
Paper Complaint OCR Agent
Reads handwritten or printed Tamil/English text from an image
and returns a clean English translation for the AI pipeline.
"""

from typing import Any, List, Optional, Union
import logging
import os

logger = logging.getLogger(__name__)

# --- EasyOCR (Primary) ---
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    logger.info("EasyOCR available.")
except ImportError:
    easyocr = None
    EASYOCR_AVAILABLE = False
    logger.warning("EasyOCR not installed. Paper OCR will use Tesseract fallback.")

_easyocr_reader: Any = None  # Use Any to satisfy IDE for optional dependency

# --- Pytesseract (Fallback) ---
try:
    import pytesseract
    from PIL import Image as PILImage
    TESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    PILImage = None
    TESSERACT_AVAILABLE = False
    logger.warning("Pytesseract not installed. OCR fallback unavailable.")

# --- Translator ---
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
    logger.info("deep-translator available.")
except ImportError:
    GoogleTranslator = None
    TRANSLATOR_AVAILABLE = False
    logger.warning("deep-translator not installed. Translation will be skipped.")


def _get_easyocr_reader() -> Optional[Any]:
    """Lazy-initialize EasyOCR reader (downloads model on first call)."""
    global _easyocr_reader
    if _easyocr_reader is None and easyocr is not None:
        try:
            logger.info("Initializing EasyOCR reader for Tamil + English (first-time model download may take a minute)...")
            _easyocr_reader = easyocr.Reader(['ta', 'en'], gpu=False)
            logger.info("EasyOCR reader ready.")
        except Exception as e:
            logger.error(f"EasyOCR initialization failed: {e}")
            _easyocr_reader = None
    return _easyocr_reader


class PaperOCRAgent:
    """
    Step 1: Extracts text from a paper complaint image (Tamil or English, handwritten or printed).
    Step 2: Detects language and translates to English.
    Output: Clean English text string ready for Feature Extraction Agent.
    """

    def extract_text(self, image_path: str) -> str:
        """Extract raw text from image using EasyOCR (primary) or Tesseract (fallback)."""
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return ""

        # Try EasyOCR first (best Tamil handwriting support)
        reader = _get_easyocr_reader()
        if reader is not None:
            try:
                results = reader.readtext(image_path, detail=0, paragraph=True)
                if results and isinstance(results, list):
                    raw_text = " ".join([str(r) for r in results]).strip()
                    logger.info(f"EasyOCR extracted {len(raw_text)} chars: '{raw_text[:80]}...'")
                    return raw_text
            except Exception as e:
                logger.error(f"EasyOCR extraction failed: {e}. Trying Tesseract fallback.")

        # Fallback to Tesseract
        tess = pytesseract
        pil_img = PILImage
        if tess is not None and pil_img is not None:
            try:
                img = pil_img.open(image_path)
                # Try Tamil + English config
                raw_text = tess.image_to_string(img, lang='tam+eng', config='--psm 6')
                if not raw_text.strip():
                    # Try English only
                    raw_text = tess.image_to_string(img, config='--psm 6')
                raw_text = raw_text.strip()
                logger.info(f"Tesseract extracted {len(raw_text)} chars: '{raw_text[:80]}...'")
                return raw_text
            except Exception as e:
                logger.error(f"Tesseract extraction failed: {e}")

        logger.warning("No OCR engine available. Returning empty string.")
        return ""

    def translate_to_english(self, text: str) -> str:
        """Translate any language text to English using deep-translator."""
        if not text.strip():
            return text

        translator_class = GoogleTranslator
        if translator_class is None:
            logger.warning("Translator unavailable. Returning text as-is.")
            return text

        try:
            # Auto-detect language and translate to English
            translated = translator_class(source='auto', target='en').translate(text)
            if translated is None:
                return text
            logger.info(f"Translation: '{text[:60]}' → '{translated[:60]}'")
            return str(translated)
        except Exception as e:
            logger.error(f"Translation failed: {e}. Returning original text.")
            return text

    def process(self, image_path: str) -> str:
        """
        Full pipeline:
        1. Extract text from image (Tamil/English handwritten/printed)
        2. Translate to English
        Returns clean English text string.
        """
        logger.info(f"PaperOCRAgent processing image: {image_path}")
        raw_text = self.extract_text(image_path)

        if not raw_text:
            logger.warning("OCR returned no text from image.")
            return ""

        english_text = self.translate_to_english(raw_text)
        logger.info(f"PaperOCRAgent final output: '{english_text[:100]}'")
        return english_text
