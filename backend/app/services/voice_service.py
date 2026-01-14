"""
Voice Service - Google Cloud Speech-to-Text and Text-to-Speech integration.

Provides speech recognition and text-to-speech capabilities using Google Cloud APIs.
"""

import logging
import io
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import Google Cloud libraries
try:
    from google.cloud import speech_v1 as speech
    from google.cloud import texttospeech_v1 as tts
    from google.api_core.exceptions import GoogleAPIError
    GCP_AVAILABLE = True
except ImportError:
    logger.warning("Google Cloud Speech/TTS libraries not installed. Voice features will use fallback.")
    GCP_AVAILABLE = False
    speech = None
    tts = None
    GoogleAPIError = Exception


class VoiceService:
    """
    Service for handling voice-related operations using Google Cloud APIs.

    Supports:
    - Speech-to-Text (STT) for voice input
    - Text-to-Speech (TTS) for voice output
    - Voice configuration and management
    """

    def __init__(self):
        """Initialize Google Cloud clients."""
        self.speech_client = None
        self.tts_client = None
        
        if GCP_AVAILABLE:
            try:
                self.speech_client = speech.SpeechClient()
                self.tts_client = tts.TextToSpeechClient()
                logger.info("Google Cloud Voice clients initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Cloud clients: {e}")
                logger.warning("Voice features will use fallback/mock implementations")
        else:
            logger.warning("Google Cloud libraries not available. Using fallback implementations.")

    async def speech_to_text(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Convert speech audio to text using Google Cloud Speech-to-Text.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            Dict with 'text' and 'confidence' keys
        """
        if not self.speech_client:
            return self._mock_stt_response()

        try:
            # Read audio file
            with open(audio_file_path, "rb") as audio_file:
                content = audio_file.read()

            # Configure audio settings
            audio = speech.RecognitionAudio(content=content)

            # Detect audio encoding based on file extension
            file_ext = Path(audio_file_path).suffix.lower()
            encoding_map = {
                '.webm': speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                '.mp4': speech.RecognitionConfig.AudioEncoding.MP3,
                '.wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
                '.flac': speech.RecognitionConfig.AudioEncoding.FLAC,
                '.ogg': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            }
            
            encoding = encoding_map.get(file_ext, speech.RecognitionConfig.AudioEncoding.WEBM_OPUS)

            config = speech.RecognitionConfig(
                encoding=encoding,
                sample_rate_hertz=44100,  # Common for web audio
                language_code="en-CA",  # Canadian English as default
                enable_automatic_punctuation=True,
                enable_word_time_offsets=False,
            )

            # Perform speech recognition
            logger.info("Sending audio to Google Cloud Speech-to-Text")
            response = self.speech_client.recognize(config=config, audio=audio)

            # Process results
            if response.results:
                result = response.results[0]
                if result.alternatives:
                    alternative = result.alternatives[0]
                    return {
                        "text": alternative.transcript,
                        "confidence": alternative.confidence or 0.85
                    }

            # No speech detected
            logger.warning("No speech detected in audio")
            return {
                "text": "",
                "confidence": 0.0
            }

        except GoogleAPIError as e:
            logger.error(f"Google Cloud STT API error: {e}")
            raise Exception(f"Speech recognition failed: {e}")
        except Exception as e:
            logger.error(f"STT processing error: {e}")
            raise Exception(f"Failed to process speech: {e}")

    async def text_to_speech(
        self,
        text: str,
        voice: str = "en-CA-Neural2-D",
        language: str = "en-CA",
        speed: float = 1.0
    ) -> bytes:
        """
        Convert text to speech using Google Cloud Text-to-Speech.

        Args:
            text: Text to convert to speech
            voice: Voice name (e.g., "en-CA-Neural2-D")
            language: Language code (e.g., "en-CA")
            speed: Speech speed (0.25 to 4.0)

        Returns:
            Audio data as bytes (MP3 format)
        """
        if not self.tts_client:
            return self._mock_tts_response()

        try:
            # Configure TTS request
            input_text = tts.SynthesisInput(text=text)

            # Voice configuration
            voice_config = tts.VoiceSelectionParams(
                language_code=language,
                name=voice,
                ssml_gender=tts.SsmlVoiceGender.NEUTRAL
            )

            # Audio configuration
            audio_config = tts.AudioConfig(
                audio_encoding=tts.AudioEncoding.MP3,
                speaking_rate=speed,
                pitch=0.0,  # Neutral pitch
            )

            # Generate speech
            logger.info(f"Generating TTS for text (length: {len(text)})")
            response = self.tts_client.synthesize_speech(
                input=input_text,
                voice=voice_config,
                audio_config=audio_config
            )

            logger.info(f"TTS generated successfully, audio size: {len(response.audio_content)} bytes")
            return response.audio_content

        except GoogleAPIError as e:
            logger.error(f"Google Cloud TTS API error: {e}")
            raise Exception(f"Text-to-speech failed: {e}")
        except Exception as e:
            logger.error(f"TTS processing error: {e}")
            raise Exception(f"Failed to generate speech: {e}")

    async def get_available_voices(self) -> List[Dict[str, str]]:
        """
        Get list of available TTS voices.

        Returns:
            List of voice configurations
        """
        if not self.tts_client:
            return self._mock_voice_list()

        try:
            # Get voices for English (Canadian)
            voices_request = tts.ListVoicesRequest(language_code="en-CA")
            response = self.tts_client.list_voices(request=voices_request)

            voices = []
            for voice in response.voices[:10]:  # Limit to first 10 for performance
                voices.append({
                    "name": voice.name,
                    "language": voice.language_codes[0] if voice.language_codes else "en-CA",
                    "gender": voice.ssml_gender.name if voice.ssml_gender else "NEUTRAL",
                    "display_name": f"{voice.name} ({voice.ssml_gender.name})"
                })

            logger.info(f"Retrieved {len(voices)} available voices")
            return voices

        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return self._mock_voice_list()

    # ============================================
    # Fallback / Mock Implementations
    # ============================================

    def _mock_stt_response(self) -> Dict[str, Any]:
        """Mock STT response when Google Cloud is not available."""
        logger.warning("Using mock STT response (Google Cloud not configured)")
        logger.warning("To enable voice features, configure Google Cloud Speech-to-Text:")
        logger.warning("1. Install: pip install google-cloud-speech")
        logger.warning("2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        logger.warning("3. Enable Speech-to-Text API in your GCP project")
        return {
            "text": "Mock transcription: Please configure Google Cloud Speech-to-Text for actual functionality.",
            "confidence": 0.8
        }

    def _mock_tts_response(self) -> bytes:
        """Mock TTS response when Google Cloud is not available."""
        logger.warning("Using mock TTS response (Google Cloud not configured)")
        logger.warning("To enable voice features, configure Google Cloud Text-to-Speech:")
        logger.warning("1. Install: pip install google-cloud-texttospeech")
        logger.warning("2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        logger.warning("3. Enable Text-to-Speech API in your GCP project")
        # Return empty MP3 data (would normally be real audio)
        return b"mock_audio_data_mp3_placeholder"

    def _mock_voice_list(self) -> List[Dict[str, str]]:
        """Mock voice list when Google Cloud is not available."""
        return [
            {
                "name": "en-CA-Neural2-D",
                "language": "en-CA",
                "gender": "MALE",
                "display_name": "Neural Male (Mock)"
            },
            {
                "name": "en-CA-Neural2-C",
                "language": "en-CA",
                "gender": "FEMALE",
                "display_name": "Neural Female (Mock)"
            }
        ]

    # ============================================
    # Utility Methods
    # ============================================

    def get_supported_audio_formats(self) -> List[str]:
        """Get list of supported audio formats for STT."""
        return [
            "audio/webm",
            "audio/mp4",
            "audio/wav",
            "audio/flac",
            "audio/ogg"
        ]

    def validate_audio_file(self, file_path: str) -> bool:
        """Validate that audio file exists and is readable."""
        try:
            path = Path(file_path)
            return path.exists() and path.is_file() and path.stat().st_size > 0
        except Exception:
            return False
