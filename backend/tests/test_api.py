import json
import httpx
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.services.risk_engine import RiskEngine
from app.config import settings

client = TestClient(app)

def make_httpx_response(status_code=200, json_data=None, content=b"", headers=None):
    if json_data is not None:
        content = json.dumps(json_data).encode("utf-8")
        default_headers = {"content-type": "application/json"}
    else:
        default_headers = {"content-type": "audio/wav"}
    
    if headers:
        default_headers.update(headers)

    return httpx.Response(
        status_code=status_code,
        headers=default_headers,
        content=content,
        request=httpx.Request("POST", "https://api.vachana.ai/test")
    )

# -------------------------------------------------------------
# 1. Health & Configuration Tests
# -------------------------------------------------------------
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_config_missing_api_key_safe(monkeypatch):
    """Verifies that missing API key defaults safely to empty string without exposing secrets."""
    from app.config import Settings
    monkeypatch.delenv("GNANI_API_KEY", raising=False)
    test_settings = Settings(_env_file=None)
    assert test_settings.GNANI_API_KEY == ""
    assert "vachana.ai" in test_settings.GNANI_STT_ENDPOINT
    assert "vachana.ai" in test_settings.GNANI_TTS_ENDPOINT

# -------------------------------------------------------------
# 2. Risk Engine Regression Tests
# -------------------------------------------------------------
def test_risk_engine_direct_credential_request():
    engine = RiskEngine()
    transcript = "Tell me your OTP to verify your bank account."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "HIGH"
    assert any(ind.indicator_type == "OTP_REQUEST" for ind in indicators)

def test_risk_engine_protective_advice():
    engine = RiskEngine()
    transcript = "Never share your OTP with anyone."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "LOW"

def test_risk_engine_educational_discussion():
    engine = RiskEngine()
    transcript = "Scammers impersonate police officers to frighten victims."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "LOW"

def test_risk_engine_remote_access_coercion():
    engine = RiskEngine()
    transcript = "Install this remote access application so I can fix your bank account."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "HIGH"
    assert any(ind.indicator_type == "REMOTE_ACCESS" for ind in indicators)

def test_risk_engine_urgent_payment_demand():
    engine = RiskEngine()
    transcript = "Transfer the money immediately or your account will be blocked."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "HIGH"
    assert any(ind.indicator_type == "PAYMENT_PRESSURE" for ind in indicators)

def test_risk_engine_benign_refund_instructions():
    engine = RiskEngine()
    transcript = "Please follow the official refund instructions in your bank application."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "LOW"

def test_risk_engine_ambiguous_statement():
    engine = RiskEngine()
    transcript = "Please follow the instructions to complete the verification."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) in ["LOW", "CAUTION"]

def test_risk_engine_explicit_credential_disclosure():
    engine = RiskEngine()
    transcript = "Read the OTP sent to your phone."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "HIGH"

def test_risk_engine_protective_discussion_remote_access():
    engine = RiskEngine()
    transcript = "Do not install AnyDesk if a caller asks you to."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "LOW"

def test_risk_engine_multiple_indicators():
    engine = RiskEngine()
    transcript = "I am calling from the police. Transfer the money immediately."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "HIGH"
    assert any(ind.indicator_type == "IMPERSONATION" for ind in indicators)
    assert any(ind.indicator_type == "PAYMENT_PRESSURE" for ind in indicators)

def test_risk_engine_hindi_transcript():
    engine = RiskEngine()
    # Real Gnani STT Hindi output with spaced Devanagari OTP
    transcript = "नमस्ते आपके बैंक खाते से पैसे कट रहे हैं, तुरंत अपना ओ टी पी बताइये।"
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "HIGH"
    assert any(ind.indicator_type in ["OTP_REQUEST", "PAYMENT_PRESSURE"] for ind in indicators)

def test_risk_engine_hinglish_transcript():
    engine = RiskEngine()
    transcript = "Turant apna OTP batao nahi toh account block ho jayega."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "HIGH"
    assert any(ind.indicator_type == "OTP_REQUEST" for ind in indicators)

def test_risk_engine_hindi_protective_advice():
    engine = RiskEngine()
    transcript = "अपना पासवर्ड या ओटीपी कभी किसी को मत देना।"
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "LOW"

def test_risk_engine_benign_statements_prevent_false_positives():
    engine = RiskEngine()
    benign_sentences = [
        "I am going to the bank to deposit money.",
        "Can you send the document right now?",
        "Transfer the files immediately please.",
        "Never install remote access software from unknown callers."
    ]
    for s in benign_sentences:
        indicators = engine.analyze_transcript(s)
        assert engine.calculate_risk_level(indicators) == "LOW", f"False positive on: {s}"

def test_risk_engine_cbi_digital_arrest():
    engine = RiskEngine()
    transcript = "This is CBI officer Sharma. You are under digital arrest."
    indicators = engine.analyze_transcript(transcript)
    assert engine.calculate_risk_level(indicators) == "CAUTION"
    assert any(ind.indicator_type == "IMPERSONATION" for ind in indicators)



# -------------------------------------------------------------
# 3. Upload Validation & Size Limits
# -------------------------------------------------------------
def test_empty_audio_upload():
    response = client.post(
        "/api/v1/end-to-end",
        files={"audio_file": ("empty.wav", b"", "audio/wav")},
        data={"language": "en-IN"}
    )
    assert response.status_code == 400
    assert "Empty file uploaded" in response.json()["detail"]

def test_oversized_audio_upload(monkeypatch):
    monkeypatch.setattr(settings, "MAX_AUDIO_SIZE_MB", 1)
    oversized_data = b"0" * (1024 * 1024 + 512)
    response = client.post(
        "/api/v1/end-to-end",
        files={"audio_file": ("large.wav", oversized_data, "audio/wav")},
        data={"language": "en-IN"}
    )
    assert response.status_code == 413
    assert "exceeds maximum size limit" in response.json()["detail"]

# -------------------------------------------------------------
# 4. Explicit Mock / Demo Mode Tests (When API Key is Missing)
# -------------------------------------------------------------
def test_demo_mode_when_api_key_unconfigured(monkeypatch):
    monkeypatch.setattr(settings, "GNANI_API_KEY", "")
    
    # 1. STT returns explicit demo flag and demo prefix
    stt_res = client.post(
        "/api/v1/transcribe",
        files={"audio_file": ("sample.wav", b"dummy audio", "audio/wav")},
        data={"language": "en-IN"}
    )
    assert stt_res.status_code == 200
    stt_data = stt_res.json()
    assert stt_data["is_demo"] is True
    assert "[DEMO MODE]" in stt_data["transcript"]

    # 2. TTS refuses to return fake silent audio and explains demo mode clearly
    tts_res = client.post(
        "/api/v1/synthesize",
        json={"text": "Warning. Never share OTP.", "language": "en-IN"}
    )
    assert tts_res.status_code == 400
    assert "Speech synthesis is unavailable in Demo Mode" in tts_res.json()["detail"]

    # 3. End-to-end returns is_demo=True
    e2e_res = client.post(
        "/api/v1/end-to-end",
        files={"audio_file": ("sample.wav", b"dummy audio", "audio/wav")},
        data={"language": "en-IN"}
    )
    assert e2e_res.status_code == 200
    assert e2e_res.json()["is_demo"] is True

# -------------------------------------------------------------
# 5. STT Provider Response & Malformation Tests (Key Configured)
# -------------------------------------------------------------
@patch.object(httpx.AsyncClient, "post")
def test_stt_valid_response(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "GNANI_API_KEY", "test-key-12345")
    mock_post.return_value = make_httpx_response(
        status_code=200,
        json_data={"success": True, "transcript": "Tell me your OTP immediately."}
    )
    
    response = client.post(
        "/api/v1/transcribe",
        files={"audio_file": ("audio.wav", b"content", "audio/wav")},
        data={"language": "en-IN"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transcript"] == "Tell me your OTP immediately."
    assert data["is_demo"] is False

@patch.object(httpx.AsyncClient, "post")
def test_stt_missing_transcript_field(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "GNANI_API_KEY", "test-key-12345")
    # 200 OK from provider but missing "transcript" key
    mock_post.return_value = make_httpx_response(
        status_code=200,
        json_data={"success": True, "request_id": "abc1234"}
    )
    
    response = client.post(
        "/api/v1/end-to-end",
        files={"audio_file": ("audio.wav", b"content", "audio/wav")},
        data={"language": "en-IN"}
    )
    assert response.status_code == 502
    assert "missing 'transcript' field" in response.json()["detail"]
    # Confirms provider error never becomes a LOW risk result

@patch.object(httpx.AsyncClient, "post")
def test_stt_empty_transcript_string(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "GNANI_API_KEY", "test-key-12345")
    # 200 OK with empty transcript string
    mock_post.return_value = make_httpx_response(
        status_code=200,
        json_data={"success": True, "transcript": "   "}
    )
    
    response = client.post(
        "/api/v1/end-to-end",
        files={"audio_file": ("audio.wav", b"content", "audio/wav")},
        data={"language": "en-IN"}
    )
    assert response.status_code == 502
    assert "empty transcript" in response.json()["detail"]

@patch.object(httpx.AsyncClient, "post")
def test_stt_invalid_json(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "GNANI_API_KEY", "test-key-12345")
    # 200 OK with non-JSON HTML error body
    mock_post.return_value = httpx.Response(
        status_code=200,
        content=b"<html>502 Bad Gateway from upstream CDN</html>",
        request=httpx.Request("POST", "https://api.vachana.ai")
    )
    
    response = client.post(
        "/api/v1/end-to-end",
        files={"audio_file": ("audio.wav", b"content", "audio/wav")},
        data={"language": "en-IN"}
    )
    assert response.status_code == 502
    assert "invalid (non-JSON)" in response.json()["detail"]

@patch.object(httpx.AsyncClient, "post")
def test_stt_provider_http_error(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "GNANI_API_KEY", "test-key-12345")
    mock_post.return_value = make_httpx_response(status_code=500, json_data={"error": "server failure"})
    
    response = client.post(
        "/api/v1/end-to-end",
        files={"audio_file": ("audio.wav", b"content", "audio/wav")},
        data={"language": "en-IN"}
    )
    assert response.status_code == 502
    assert "HTTP 500" in response.json()["detail"]

@patch.object(httpx.AsyncClient, "post")
def test_stt_provider_timeout(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "GNANI_API_KEY", "test-key-12345")
    mock_post.side_effect = httpx.TimeoutException("Read timed out")
    
    response = client.post(
        "/api/v1/end-to-end",
        files={"audio_file": ("audio.wav", b"content", "audio/wav")},
        data={"language": "en-IN"}
    )
    assert response.status_code == 504
    assert "timed out" in response.json()["detail"]

# -------------------------------------------------------------
# 6. Timbre TTS Mocked Integration Tests
# -------------------------------------------------------------
@patch.object(httpx.AsyncClient, "post")
def test_tts_valid_synthesis(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "GNANI_API_KEY", "test-key-12345")
    binary_wav = b"RIFF....WAVEfmt ....data...."
    mock_post.return_value = make_httpx_response(
        status_code=200,
        content=binary_wav,
        headers={"content-type": "audio/wav"}
    )
    
    response = client.post(
        "/api/v1/synthesize",
        json={"text": "Never share your OTP.", "language": "en-IN"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_demo"] is False
    assert len(data["audio_content"]) > 0

@patch.object(httpx.AsyncClient, "post")
def test_tts_empty_audio_content(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "GNANI_API_KEY", "test-key-12345")
    mock_post.return_value = make_httpx_response(
        status_code=200,
        content=b"",
        headers={"content-type": "audio/wav"}
    )
    
    response = client.post(
        "/api/v1/synthesize",
        json={"text": "Never share your OTP.", "language": "en-IN"}
    )
    assert response.status_code == 502
    assert "empty audio content" in response.json()["detail"]

@patch.object(httpx.AsyncClient, "post")
def test_tts_provider_http_error(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "GNANI_API_KEY", "test-key-12345")
    mock_post.return_value = make_httpx_response(status_code=400, json_data={"error": "invalid model"})
    
    response = client.post(
        "/api/v1/synthesize",
        json={"text": "Never share your OTP.", "language": "en-IN"}
    )
    assert response.status_code == 502
    assert "HTTP 400" in response.json()["detail"]

@patch.object(httpx.AsyncClient, "post")
def test_tts_provider_timeout(mock_post, monkeypatch):
    monkeypatch.setattr(settings, "GNANI_API_KEY", "test-key-12345")
    mock_post.side_effect = httpx.TimeoutException("TTS connection timed out")
    
    response = client.post(
        "/api/v1/synthesize",
        json={"text": "Never share your OTP.", "language": "en-IN"}
    )
    assert response.status_code == 504
    assert "timed out" in response.json()["detail"]
