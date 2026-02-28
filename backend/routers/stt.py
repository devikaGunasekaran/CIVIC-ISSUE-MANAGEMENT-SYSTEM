import os
import shutil
import logging
import time
import json
import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/stt", tags=["stt"])
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("[STT] Gemini configured successfully")
    except Exception as e:
        logger.error(f"[STT] Config error: {e}")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    print(f"\n[STT] Received upload request: {audio.filename} ({audio.content_type})")
    
    if not GEMINI_API_KEY:
        print("[STT] ERROR: No Gemini API Key")
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    file_path = f"{UPLOAD_DIR}/stt_{audio.filename}"
    try:
        # Ensure we're at the start of the file
        await audio.seek(0)
        
        # Save temp file
        print(f"[STT] Saving file to {file_path}...")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        file_size = os.path.getsize(file_path)
        print(f"[STT] Saved {file_size} bytes")
        
        if file_size == 0:
            raise Exception("Uploaded audio file is empty (0 bytes)")

        # Configure Gemini locally for the request to avoid global state issues
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Gemini STT
        model = genai.GenerativeModel('models/gemini-flash-latest')
        print(f"[STT] Uploading to Gemini API (mime_type='audio/wav')...")
        
        try:
            audio_file = genai.upload_file(path=file_path, mime_type="audio/wav")
            print(f"[STT] Gemini Upload OK. Name: {audio_file.name}")
        except Exception as upload_err:
            print(f"[STT] Gemini Upload FAILED: {upload_err}")
            raise Exception(f"Failed to upload to Gemini: {upload_err}")
        
        # Poll for file to be ready
        max_retries = 30
        retries = 0
        while audio_file.state.name == "PROCESSING" and retries < max_retries:
            print(f"[STT] Gemini Processing... (attempt {retries+1})")
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)
            retries += 1

        if audio_file.state.name == "FAILED":
            raise Exception(f"Gemini audio processing failed: {audio_file.state.name}")
        
        if audio_file.state.name != "ACTIVE":
             print(f"[STT] WARNING: File state is {audio_file.state.name} after polling")

        print(f"[STT] Analyzing with prompt...")
        prompt = """Analyze the following audio recording of a civic complaint in Chennai.
        
Context:
1. The user may speak in Tamil, English, or "Tanglish" (Tamil-English mix).
2. Transcription MUST be accurate to what is spoken.
3. If Tamil is spoken, use Tamil script.
4. If Tanglish is used (e.g., "street light work aagala"), keep it as spoken.
5. Capture critical technical/infrastructure words clearly: "pothole", "garbage", "EB problem", "transformer", "water stagnation", "theru vilakku".

Output Format (JSON):
{
  "transcription": "...",
  "confidence": 0.95,
  "language_detected": "...",
  "is_clear": true
}
Only return the JSON. No other text."""

        response = model.generate_content([prompt, audio_file])
        text = response.text.strip()
        print(f"[STT] Gemini responded: {text[:100]}...")
        
        # Robust JSON extraction
        if "{" in text and "}" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            json_text = text[start:end]
            result = json.loads(json_text)
        else:
            result = {
                "transcription": text,
                "confidence": 0.5,
                "language_detected": "Unknown",
                "is_clear": False
            }
        
        print(f"[STT] SUCCESS: {result.get('transcription', '')[:50]}")
        return result

    except Exception as e:
        full_error = traceback.format_exc()
        error_msg = f"Inference Error: {str(e)}\n{full_error}"
        print(f"[STT] CRITICAL ERROR:\n{error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        # Cleanup
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
