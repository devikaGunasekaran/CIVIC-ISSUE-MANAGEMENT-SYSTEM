from fastapi import APIRouter, UploadFile, File
from ..services.stt_service import stt_service

router = APIRouter(prefix="/stt", tags=["stt"])

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    return await stt_service.transcribe(audio)
