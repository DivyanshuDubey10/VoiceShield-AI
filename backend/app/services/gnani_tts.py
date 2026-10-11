from typing import Tuple, Optional
import httpx
import base64
from fastapi import HTTPException
from app.config import settings
from app.core.logging import logger

class GnaniTTSService:
    """
    Client for Gnani Timbre Text-to-Speech REST API.
    Endpoint: https://api.vachana.ai/api/v1/tts/inference
    """
    async def generate_audio(
        self, 
        text: str, 
        language: str = "en-IN", 
        voice: Optional[str] = None
    ) -> Tuple[str, bool]:
        """
        Synthesizes text into speech. Returns a tuple of (base64_audio_content, is_demo).
        """
        # When credentials are not configured, do not synthesize silent fake audio
        if not settings.GNANI_API_KEY:
            logger.info("Gnani API key missing. Refusing to synthesize silent fake audio.")
            raise HTTPException(
                status_code=400,
                detail="Speech synthesis is unavailable in Demo Mode. Add GNANI_API_KEY to your .env file to enable live voice generation."
            )

        headers = {
            "X-API-Key-ID": settings.GNANI_API_KEY,
            "Content-Type": "application/json"
        }
        
        selected_voice = voice or "Nalini"
        tts_lang_map = {
            "hinglish": "hi-IN",
            "indic-auto": "hi-IN",
            "hindi": "hi-IN",
            "english": "en-IN",
        }
        effective_language = tts_lang_map.get(language.lower(), language)

        payload = {
            "text": text,
            "model": "timbre-v2.5",
            "voice": selected_voice,
            "language_code": effective_language,
            "audio_config": {
                "container": "wav",
                "encoding": "linear_pcm",
                "num_channels": 1,
                "sample_rate": 16000
            }
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    settings.GNANI_TTS_ENDPOINT,
                    headers=headers,
                    json=payload
                )
                
            response.raise_for_status()
            
            # Binary audio response verification
            if not response.content or len(response.content) == 0:
                logger.error("Gnani TTS returned empty content body")
                raise HTTPException(
                    status_code=502,
                    detail="TTS provider returned empty audio content."
                )

            # Check if binary audio or JSON envelope
            content_type = response.headers.get("content-type", "").lower()
            if "audio" in content_type or "octet-stream" in content_type:
                audio_b64 = base64.b64encode(response.content).decode("utf-8")
                return (audio_b64, False)
            else:
                try:
                    result = response.json()
                    audio_b64 = result.get("audio_content") or result.get("audio") or ""
                    if not audio_b64:
                        raise ValueError("No audio field found in response JSON")
                    return (audio_b64, False)
                except Exception:
                    # If not JSON, but content is non-empty, encode raw bytes
                    audio_b64 = base64.b64encode(response.content).decode("utf-8")
                    return (audio_b64, False)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Gnani TTS HTTP {e.response.status_code} error: {e.response.text}")
            raise HTTPException(
                status_code=502,
                detail=f"TTS provider returned an error: HTTP {e.response.status_code}"
            )
        except httpx.TimeoutException:
            logger.error("Gnani TTS request timed out")
            raise HTTPException(
                status_code=504,
                detail="TTS service timed out after 20 seconds."
            )
        except httpx.RequestError as e:
            logger.error(f"Gnani TTS connection error: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail="Unable to establish connection to TTS provider."
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Gnani TTS unexpected error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during speech synthesis."
            )
