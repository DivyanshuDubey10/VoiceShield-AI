from pydantic import BaseModel
from typing import List, Optional

class Evidence(BaseModel):
    excerpt: str
    rationale: str
    severity: str  # "HIGH", "MEDIUM", "LOW"
    indicator_type: str

class AnalysisResponse(BaseModel):
    risk_level: str  # "LOW", "CAUTION", "HIGH"
    summary: str
    indicators: List[Evidence]
    guidance: str
    limitations: str
    is_demo: bool = False

class STTResponse(BaseModel):
    transcript: str
    language: str
    confidence: Optional[float] = None
    is_demo: bool = False

class TTSResponse(BaseModel):
    audio_content: str  # base64 encoded audio
    content_type: str = "audio/wav"
    is_demo: bool = False
