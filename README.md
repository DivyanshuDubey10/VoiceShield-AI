# VoiceShield AI
## Multilingual Voice Scam Intelligence and Prevention System

VoiceShield AI is an explainable voice-scam analysis application designed to transcribe suspicious call recordings, identify social-engineering manipulation patterns, highlight evidence, and deliver spoken safety guidance in Indian languages.

---

### Core Architecture & Flow

```
[Audio Recording]
       │
       ▼
[Gnani Prisma STT] ──────► Transcribes spoken audio into text
       │
       ▼
[Risk Engine] ───────────► Evaluates evidence with explainable rules
       │
       ▼
[Safety Guidance] ───────► Formulates actionable advice
       │
       ▼
[Gnani Timbre TTS] ──────► Synthesizes spoken advisory audio
```

1. **Speech-to-Text (STT):** Calls Gnani Prisma (`/stt/v3`) to convert audio into text. If an API key is not configured, it safely operates in **Demo Mode** with pre-configured scam scenarios.
2. **Explainable Risk Engine:** Evaluates text sentence-by-sentence using named social engineering heuristics (OTP harvesting, payment pressure, authority impersonation, remote access installation) while filtering out defensive and educational discussions.
3. **Text-to-Speech (TTS):** Uses Gnani Timbre (`/api/v1/tts/inference` with model `timbre-v2.5`) to convert safety advice into audible speech.
4. **Cybersecurity Dashboard:** React + TypeScript + Tailwind UI showing risk rating, exact evidence quotes, and playable guidance.

---

### Technology Stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, HTTPX, Pytest
- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons
- **Speech APIs:** Gnani Prisma (STT v3), Gnani Timbre (TTS v2.5)

---

### Setup & Running Locally (Windows 11)

#### 1. Backend Setup
From the repository root:
```powershell
cd backend

# Create virtual environment (using Python 3.12)
& "C:\Users\user\AppData\Local\Python\pythoncore-3.12-64\python.exe" -m venv .venv

# Install dependencies
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

#### 2. Environment Configuration
Copy `.env.example` to `.env` in the project root:
```powershell
copy .env.example .env
```
Inside `.env`, configure your Gnani credentials:
```env
GNANI_API_KEY=your_actual_key_here
```
*Note: If `GNANI_API_KEY` is blank, VoiceShield automatically operates in safe Demo Mode with mock transcription and synthesis to protect your API quota.*

#### 3. Run Backend Server
```powershell
cd backend
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --reload
```
Health endpoint is accessible at `http://localhost:8000/health`.

#### 4. Frontend Setup & Run
In a separate terminal:
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

### Running Automated Tests
Run the test suite safely without consuming API credits:
```powershell
cd backend
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

---

### Key Design Principles

1. **Explainability over Black-Box Scoring:** Instead of a mysterious single number, VoiceShield pinpoints the exact sentence that triggered the alert and explains *why* it is dangerous.
2. **Context-Aware Defenses:** Distinguishes between scammers demanding an OTP and legitimate security warnings telling people *never* to share an OTP.
3. **Zero Data Retention:** Audio uploads are processed in-memory and ephemerally. Raw audio bytes are never saved to disk or logged.
