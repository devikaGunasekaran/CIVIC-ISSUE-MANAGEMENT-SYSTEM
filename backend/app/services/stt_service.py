import os
import shutil
import logging
import time
import json
import google.generativeai as genai
from fastapi import UploadFile, File, HTTPException
from ..core.config import settings

logger = logging.getLogger(__name__)

class STTService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                logger.info("[STT] Gemini configured successfully")
            except Exception as e:
                logger.error(f"[STT] Config error: {e}")

    async def transcribe(self, audio: UploadFile):
        if not settings.GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")

        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = f"{upload_dir}/stt_{audio.filename}"
        
        try:
            await audio.seek(0)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(audio.file, buffer)
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                raise Exception("Uploaded audio file is empty")

            model = genai.GenerativeModel('gemini-2.5-flash')
            audio_file = genai.upload_file(path=file_path, mime_type="audio/wav")
            
            # Poll
            retries = 0
            import asyncio
            while audio_file.state.name == "PROCESSING" and retries < 30:
                await asyncio.sleep(1)
                audio_file = genai.get_file(audio_file.name)
                retries += 1

            prompt = """Analyze the following audio recording of a civic complaint in Chennai.
            The speaker may use Tamil, English, or a mix (Tanglish). 
            Transcribe exactly what is spoken.
            Common technical terms: "pothole", "kuli/kuzhi", "garbage", "EB problem", "transformer", "water stagnation", "street light", "road damage".
            
            Return ONLY a JSON object: {"transcription": "...", "confidence": 0.95, "language_detected": "Tamil/English/Tanglish", "is_clear": true}"""

            response = model.generate_content([prompt, audio_file])
            text = response.text.strip()
            
            # Simple JSON parse
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return {"transcription": text}

        except Exception as e:
            logger.error(f"[STT] Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

stt_service = STTService()
