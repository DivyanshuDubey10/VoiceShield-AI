from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from app.schemas.requests import TTSRequest, AnalysisRequest
from app.schemas.responses import STTResponse, TTSResponse, AnalysisResponse
from app.services.gnani_stt import GnaniSTTService
from app.services.gnani_tts import GnaniTTSService
from app.services.risk_engine import RiskEngine
from app.services.safety_guidance import SafetyGuidanceService
from app.config import settings

router = APIRouter()

stt_service = GnaniSTTService()
tts_service = GnaniTTSService()
risk_engine = RiskEngine()
guidance_service = SafetyGuidanceService()

async def safe_read(upload_file: UploadFile, max_size_mb: int) -> bytes:
    """
    Reads an uploaded file in 1MB chunks and verifies size limits.
    Prevents memory exhaustion from oversized audio uploads.
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    content = b""
    while True:
        chunk = await upload_file.read(1024 * 1024)
        if not chunk:
            break
        content += chunk
        if len(content) > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file exceeds maximum size limit of {max_size_mb}MB."
            )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded."
        )
    
    # Rewind pointer so downstream services can read file content if needed
    await upload_file.seek(0)
    return content

@router.post("/transcribe", response_model=STTResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = Form("en-IN")
):
    """Transcribes uploaded audio using Gnani Prisma STT."""
    await safe_read(audio_file, settings.MAX_AUDIO_SIZE_MB)
    transcript, is_demo = await stt_service.transcribe(audio_file, language)
    return STTResponse(transcript=transcript, language=language, is_demo=is_demo)

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_transcript(request: AnalysisRequest):
    """Analyzes a transcript for voice scam indicators using deterministic rules."""
    indicators = risk_engine.analyze_transcript(request.transcript)
    risk_level = risk_engine.calculate_risk_level(indicators)
    guidance = guidance_service.generate_guidance(risk_level, indicators)
    
    return AnalysisResponse(
        risk_level=risk_level,
        summary="Transcript analysis completed.",
        indicators=indicators,
        guidance=guidance,
        limitations="Advisory analysis based on pattern matching. Does not definitively authenticate callers or prove fraud.",
        is_demo=False
    )

@router.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """Synthesizes safety guidance into speech using Gnani Timbre TTS."""
    audio_b64, is_demo = await tts_service.generate_audio(
        text=request.text, 
        language=request.language,
        voice=request.voice
    )
    return TTSResponse(audio_content=audio_b64, is_demo=is_demo)

@router.post("/end-to-end", response_model=AnalysisResponse)
async def end_to_end_analysis(
    audio_file: UploadFile = File(...),
    language: str = Form("en-IN")
):
    """
    End-to-end scam intelligence pipeline:
    1. Transcribes audio with Gnani Prisma STT
    2. Identifies social engineering patterns with RiskEngine
    3. Generates actionable safety guidance
    """
    await safe_read(audio_file, settings.MAX_AUDIO_SIZE_MB)
    
    transcript, is_demo = await stt_service.transcribe(audio_file, language)
    indicators = risk_engine.analyze_transcript(transcript)
    risk_level = risk_engine.calculate_risk_level(indicators)
    guidance = guidance_service.generate_guidance(risk_level, indicators)
    
    summary_text = f"Transcribed Text: '{transcript}'"
    
    return AnalysisResponse(
        risk_level=risk_level,
        summary=summary_text,
        indicators=indicators,
        guidance=guidance,
        limitations="Advisory analysis based on pattern matching. Does not definitively authenticate callers or prove fraud.",
        is_demo=is_demo
    )
