from typing import Optional
from pydantic import BaseModel

class TTSRequest(BaseModel):
    text: str
    language: str = "en-IN"
    voice: Optional[str] = None

class AnalysisRequest(BaseModel):
    transcript: str
    language: str = "en-IN"
