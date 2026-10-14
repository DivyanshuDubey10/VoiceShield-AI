from typing import Tuple
import httpx
from fastapi import UploadFile, HTTPException
from app.config import settings
from app.core.logging import logger

class GnaniSTTService:
    """
    Client for Gnani Prisma Speech-to-Text REST API (v3).
    """
    async def transcribe(self, audio_file: UploadFile, language: str = "en-IN") -> Tuple[str, bool]:
        """
        Transcribes audio using Gnani Prisma STT.
        Returns a tuple: (transcript, is_demo).
        """
        # If API key is not configured, explicitly operate in demo mode
        if not settings.GNANI_API_KEY:
            logger.info("Gnani API key unconfigured. Returning explicit demo transcription.")
            return (
                "[DEMO MODE] Hello, this is your bank. Please share the OTP sent to your phone immediately to verify your account.",
                True
            )

        headers = {
            "X-API-Key-ID": settings.GNANI_API_KEY
        }
        
        content = await audio_file.read()
        files = {
            "audio_file": (audio_file.filename or "recording.wav", content, audio_file.content_type or "audio/wav")
        }
        # Map friendly language codes to Gnani supported BCP-47 codes
        lang_map = {
            "hinglish": "indic-auto",
            "hindi": "hi-IN",
            "english": "en-IN",
        }
        effective_language = lang_map.get(language.lower(), language)

        data = {
            "language_code": effective_language,
            "format": "transcribe"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    settings.GNANI_STT_ENDPOINT,
                    headers=headers,
                    files=files,
                    data=data
                )
                
            response.raise_for_status()
            
            try:
                result = response.json()
            except Exception as e:
                logger.error(f"Gnani STT invalid JSON: {str(e)}")
                raise HTTPException(
                    status_code=502,
                    detail="Transcription provider returned an invalid (non-JSON) response."
                )
            
            if not isinstance(result, dict):
                logger.error("Gnani STT returned non-dictionary response")
                raise HTTPException(
                    status_code=502,
                    detail="Transcription provider returned an unexpected data structure."
                )

            if "transcript" not in result:
                logger.error(f"Gnani STT response missing 'transcript' key. Keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")
                raise HTTPException(
                    status_code=502,
                    detail="Transcription provider response is missing 'transcript' field."
                )

            transcript = result["transcript"]
            if not isinstance(transcript, str):
                logger.error("Gnani STT returned non-string transcript")
                raise HTTPException(
                    status_code=502,
                    detail="Transcription provider returned an unexpected transcript format."
                )

            if not transcript.strip():
                logger.error("Gnani STT returned empty transcript string")
                raise HTTPException(
                    status_code=502,
                    detail="Transcription provider returned an empty transcript. Check audio clarity or format."
                )

            return (transcript.strip(), False)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Gnani STT HTTP {e.response.status_code} error")
            raise HTTPException(
                status_code=502,
                detail=f"Transcription provider returned an error: HTTP {e.response.status_code}"
            )
        except httpx.TimeoutException:
            logger.error("Gnani STT request timed out")
            raise HTTPException(
                status_code=504,
                detail="Transcription service timed out after 30 seconds."
            )
        except httpx.RequestError as e:
            logger.error(f"Gnani STT network connection error: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail="Unable to establish connection to transcription provider."
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Gnani STT unexpected error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during transcription processing."
            )
