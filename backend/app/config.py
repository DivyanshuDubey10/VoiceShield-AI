from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate repository root deterministically regardless of execution working directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ROOT_ENV_PATH = PROJECT_ROOT / ".env"
BACKEND_ENV_PATH = PROJECT_ROOT / "backend" / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "VoiceShield AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Gnani API Configuration
    GNANI_API_KEY: str = ""
    GNANI_STT_ENDPOINT: str = "https://api.vachana.ai/stt/v3"
    GNANI_TTS_ENDPOINT: str = "https://api.vachana.ai/api/v1/tts/inference"
    
    # Upload & Security Limits
    MAX_AUDIO_SIZE_MB: int = 20
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=(str(ROOT_ENV_PATH), str(BACKEND_ENV_PATH)),
        extra="ignore"
    )

settings = Settings()
