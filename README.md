# VoiceShield AI
## Multilingual Voice Scam Intelligence and Prevention System
**Submission for the Great Indian AI Internship Challenge — Gnani AI**

VoiceShield AI is an explainable, multilingual cybersecurity intelligence dashboard designed to transcribe suspicious phone call recordings, detect social-engineering manipulation patterns in Indian contexts (Hindi, Hinglish, and English), highlight verbatim evidence, and generate actionable spoken guidance to prevent financial fraud.

---

### Table of Contents
1. [Problem Statement](#problem-statement)
2. [How It Works (End-to-End Workflow)](#how-it-works-end-to-end-workflow)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Local Setup & Configuration (Windows PowerShell)](#local-setup--configuration-windows-powershell)
6. [Environment Variables](#environment-variables)
7. [Demo Mode vs. Live Provider Mode](#demo-mode-vs-live-provider-mode)
8. [Running Automated Verification Tests](#running-automated-verification-tests)
9. [Privacy Safeguards & Security Limits](#privacy-safeguards--security-limits)
10. [Known Limitations & Integration Status](#known-limitations--integration-status)
11. [How to Demonstrate the Project](#how-to-demonstrate-the-project)

---

### Problem Statement

Voice scam syndicates in India exploit fear, urgency, and technical confusion to manipulate citizens into:
- Disclosing one-time passwords (OTPs) and verification codes.
- Transferring money under manufactured threats (fake CBI/police "digital arrest", impending electricity disconnection).
- Installing dangerous remote-desktop applications (AnyDesk, TeamViewer) to drain bank accounts.

Victims need immediate, plain-language guidance in their language before taking irreversible action. Most scam detection tools rely on opaque black-box scoring; VoiceShield AI emphasizes **explainability**, isolating the exact sentence of concern so users understand *why* a call is suspicious.

---

### How It Works (End-to-End Workflow)

```
[Audio Recording (.wav, .mp3, .m4a, .ogg)]
                 │
                 ▼
       [FastAPI Backend Router]
                 │  (Enforces 20MB limit & in-memory streaming)
                 ▼
       [Gnani Prisma STT v3] ────────► Transcribes audio into Hindi/Hinglish/English
                 │
                 ▼
       [Explainable Risk Engine] ────► Evaluates sentences against scam tactics:
                 │                     • OTP/Verification Code Disclosures
                 │                     • High-Pressure Financial Threats
                 │                     • Authority Impersonation (Police/CBI)
                 │                     • Coercive Remote Access Tools
                 │                     • Filters out protective & educational advice
                 ▼
       [Safety Guidance Service] ────► Synthesizes clear advisory and safe next steps
                 │
                 ▼
       [Gnani Timbre TTS v2.5] ──────► Converts safety advice into audible Indic speech
                 │
                 ▼
       [Cybersecurity Dashboard] ────► Displays Verdict, Evidence Excerpts, & Audio Player
```

1. **Audio Ingestion:** User uploads a suspicious call recording (supports English, Hindi, and auto-detect/Hinglish).
2. **Transcription:** Sent to **Gnani Prisma STT** (`/stt/v3`). If credentials are not configured, it executes in explicit **Demo Mode**.
3. **Deterministic Analysis:** The **RiskEngine** extracts exact verbatim quotes and categorizes severity (`HIGH`, `CAUTION`, `LOW`). Sentences giving safety advice (e.g., *"Never share your OTP"*) are recognized and filtered to prevent false alarms.
4. **Actionable Advisory:** Formulates clear instructions (e.g., *"Hang up immediately and contact your bank via official channels"*).
5. **Speech Synthesis:** **Gnani Timbre TTS** (`/api/v1/tts/inference`) synthesizes guidance in audio format for playback.

---

### System Architecture

The project consists of a decoupled two-tier architecture:
- **Frontend (`/frontend`):** Modern React 18 single-page application built with TypeScript, Vite, and Tailwind CSS. Provides a clean, dark-mode cybersecurity interface with zero stored credentials.
- **Backend (`/backend`):** High-performance FastAPI server running Python 3.12, managing request validation, ephemeral file processing, deterministic pattern matching, and HTTPX communication with Gnani AI speech endpoints.

---

### Technology Stack

| Layer | Component | Version / Details |
|---|---|---|
| **Frontend** | React, TypeScript, Vite | React 18.2, TypeScript 5.2, Vite 5.4 |
| **Styling** | Tailwind CSS, Lucide Icons | Responsive dark theme, Lucide React icons |
| **Backend** | Python, FastAPI, Uvicorn | Python 3.12, FastAPI 0.104, Uvicorn 0.24 |
| **Validation** | Pydantic v2, Pydantic-Settings | Strict schemas for requests, responses, and configuration |
| **HTTP Client** | HTTPX (Async) | Async connection pooling with 30s timeouts |
| **Testing** | Pytest, Pytest-Asyncio | 34 automated unit, regression, and mock tests |
| **Speech STT** | Gnani Prisma REST API | v3 endpoint (`https://api.vachana.ai/stt/v3`) |
| **Speech TTS** | Gnani Timbre REST API | v2.5 inference (`https://api.vachana.ai/api/v1/tts/inference`) |

---

### Local Setup & Configuration (Windows PowerShell)

#### Prerequisites
- Windows 10/11 with PowerShell
- Python 3.12+ installed
- Node.js 18+ and npm installed

#### 1. Backend Setup
From the repository root (`VoiceSheild`):
```powershell
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Environment Configuration
Copy `.env.example` to `.env` in the repository root:
```powershell
copy ..\.env.example ..\.env
```
Open `.env` and set your credentials if available:
```env
GNANI_API_KEY=your_gnani_api_key_here
GNANI_STT_ENDPOINT=https://api.vachana.ai/stt/v3
GNANI_TTS_ENDPOINT=https://api.vachana.ai/api/v1/tts/inference
MAX_AUDIO_SIZE_MB=20
FRONTEND_ORIGIN=http://localhost:5173
```
*(Note: If `GNANI_API_KEY` is left blank, VoiceShield operates safely in Demo Mode.)*

#### 3. Start Backend Server
```powershell
cd backend
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --reload
```
The API is available at `http://localhost:8000`. Health check: `http://localhost:8000/health`.

#### 4. Frontend Setup & Start
Open a **new Windows PowerShell window**:
```powershell
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

### Environment Variables

| Variable | Default Value | Purpose |
|---|---|---|
| `GNANI_API_KEY` | `""` (Empty string) | Authentication key for Gnani Prisma STT and Timbre TTS. |
| `GNANI_STT_ENDPOINT` | `https://api.vachana.ai/stt/v3` | Gnani Prisma Speech-to-Text v3 endpoint. |
| `GNANI_TTS_ENDPOINT` | `https://api.vachana.ai/api/v1/tts/inference` | Gnani Timbre Text-to-Speech v2.5 endpoint. |
| `MAX_AUDIO_SIZE_MB` | `20` | Strict file upload limit to prevent memory exhaustion. |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | Allowed origin for FastAPI CORS middleware. |

---

### Demo Mode vs. Live Provider Mode

VoiceShield explicitly distinguishes between simulated and live provider operations:

| Feature | Demo Mode (`GNANI_API_KEY` blank) | Live Provider Mode (`GNANI_API_KEY` set) |
|---|---|---|
| **UI Banner** | Amber "Demo Mode Active" badge displayed | Green "Live Provider Mode" badge displayed |
| **Transcription** | Uses mock scam scenario with `[DEMO MODE]` prefix | Real-time transcription via Gnani Prisma v3 |
| **RiskEngine** | Real deterministic rules run on transcript | Real deterministic rules run on transcript |
| **Speech TTS** | Returns descriptive notice: *"Speech synthesis is unavailable in Demo Mode. Add GNANI_API_KEY to enable live voice generation."* | Synthesizes spoken advisory via Gnani Timbre v2.5 |
| **Credit Safety** | Consumes 0 API credits; safe for rehearsals | Consumes Gnani provider credits |

---

### Running Automated Verification Tests

#### Backend Test Suite (34 Tests)
Run unit tests, risk engine regression cases, and mocked integration tests without consuming credits:
```powershell
cd backend
$env:PYTHONPATH="backend"
.\.venv\Scripts\python.exe -m pytest tests/ -v
```
All 34 tests validate:
- Health check and environment configuration safety.
- 10 distinct RiskEngine social-engineering scenarios.
- Hindi, Hinglish, and English pattern recognition.
- Filtering of educational discussions and protective warnings.
- Max file size enforcement (20MB) and empty upload rejection.
- Empty transcript and empty synthesis text request validation.
- Gnani STT and TTS timeout, malformed JSON, and HTTP error handling.

#### Frontend Production Build
```powershell
cd frontend
npm run build
```
Validates TypeScript type safety and bundles assets with Vite.

---

### Privacy Safeguards & Security Limits

1. **Zero Data Retention:** Audio uploads are processed purely in-memory (`bytes`) and forwarded to the transcription service. Audio files are never written to disk or stored in local databases.
2. **Sanitized Logging:** Application logs record error codes and request counts. Raw audio buffers, user transcripts, and `X-API-Key-ID` headers are never printed to console or logs.
3. **Upload Size Restrictions:** Hard 20MB limit enforced in chunks (`1024 * 1024` bytes) to protect against memory exhaustion attacks (HTTP 413).
4. **No Frontend Secrets:** API keys reside exclusively in the backend `.env` file. No provider credentials exist in React code or bundle artifacts.

---

### Known Limitations & Integration Status

- **Integration Verification Status:** The Gnani Prisma STT v3 and Timbre TTS v2.5 integrations have been implemented to official Gnani specifications (`X-API-Key-ID`, multipart `audio_file`, `language_code`, `timbre-v2.5` model) and fully verified via automated mock tests (`httpx`). Live billable requests were not executed during audit to protect API quota.
- **Explainable Rule-Based Engine:** Analysis is performed by deterministic heuristics rather than an opaque LLM or reasoning model. This provides explainability and low latency, but does not identify callers or prove criminal intent in a legal sense.
- **Evon Reasoning:** Evon LLM reasoning is not integrated. The system intentionally uses explainable deterministic pattern matching.

---

### How to Demonstrate the Project

1. **Start the Servers:** Ensure backend is running on port 8000 and frontend on port 5173.
2. **Open Dashboard:** Navigate to `http://localhost:5173`.
3. **Select Language:** Choose `Auto Detect / Hinglish`, `Hindi`, or `English`.
4. **Upload Audio:** Select a sample recording (under 20MB).
5. **Run Analysis:** Click **Analyze Audio**.
6. **Review Findings:**
   - Note the **Verdict** (HIGH, CAUTION, or SAFE).
   - Review **Transcribed Audio** with one-click copy.
   - Inspect the **Scam Indicators**, showing the verbatim quote and rationale.
   - Listen to or read the **Recommended Action**.
   - Export the complete report via **Export JSON**.
