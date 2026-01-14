"""
Voice API Routes - Speech-to-Text and Text-to-Speech endpoints.

Endpoints:
- POST /api/voice/stt - Convert speech to text
- POST /api/voice/tts - Convert text to speech
- GET /api/voice/voices - Get available TTS voices
"""

import logging
import tempfile
import os
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.voice_service import VoiceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])


# ============================================
# Pydantic Models
# ============================================

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "en-US-Neural2-D"
    language: Optional[str] = "en-US"
    speed: Optional[float] = 1.0

class VoiceInfo(BaseModel):
    name: str
    language: str
    gender: str
    display_name: str

class STTResponse(BaseModel):
    text: str
    confidence: float

class VoicesResponse(BaseModel):
    voices: List[VoiceInfo]


# ============================================
# Voice Endpoints
# ============================================

@router.post("/stt", response_model=STTResponse)
async def speech_to_text(
    audio: UploadFile = File(...)
):
    """
    Convert speech audio to text using Google Cloud Speech-to-Text.

    Accepts audio files in various formats (webm, mp4, wav, etc.)
    Returns transcribed text and confidence score.
    """
    if not audio:
        raise HTTPException(status_code=400, detail="No audio file provided")

    # Validate file type
    allowed_types = [
        "audio/webm", "audio/mp4", "audio/wav", "audio/mpeg",
        "audio/ogg", "audio/flac"
    ]

    if audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: {audio.content_type}. Supported: {', '.join(allowed_types)}"
        )

    # Validate file size (max 25MB for Google Cloud STT)
    max_size = 25 * 1024 * 1024  # 25MB
    file_size = 0
    content = await audio.read()

    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file too large: {len(content)} bytes. Maximum: {max_size} bytes"
        )

    try:
        voice_service = VoiceService()

        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Process speech to text
            result = await voice_service.speech_to_text(temp_file_path)

            return STTResponse(
                text=result.get("text", "").strip(),
                confidence=result.get("confidence", 0.0)
            )

        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"STT processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Speech-to-text processing failed: {str(e)}"
        )


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using Google Cloud Text-to-Speech.

    Returns audio stream (MP3 format).
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text content is required")

    if len(request.text) > 5000:
        raise HTTPException(
            status_code=400,
            detail="Text too long. Maximum 5000 characters allowed."
        )

    try:
        voice_service = VoiceService()

        # Generate speech
        audio_content = await voice_service.text_to_speech(
            text=request.text,
            voice=request.voice,
            language=request.language,
            speed=request.speed
        )

        # Return audio as streaming response
        return StreamingResponse(
            iter([audio_content]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Content-Length": str(len(audio_content))
            }
        )

    except Exception as e:
        logger.error(f"TTS processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Text-to-speech processing failed: {str(e)}"
        )


@router.get("/voices", response_model=VoicesResponse)
async def get_available_voices():
    """
    Get list of available Text-to-Speech voices.

    Returns voices supported by Google Cloud Text-to-Speech.
    """
    try:
        voice_service = VoiceService()
        voices = await voice_service.get_available_voices()

        return VoicesResponse(voices=voices)

    except Exception as e:
        logger.error(f"Error fetching voices: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch available voices: {str(e)}"
        )