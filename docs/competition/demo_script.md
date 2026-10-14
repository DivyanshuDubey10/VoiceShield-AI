# VoiceShield AI — Competition Submission Materials
## Great Indian AI Internship Challenge organized by Gnani AI

---

## Part A: Project Summary

- **Project Title:** VoiceShield AI — Multilingual Voice Scam Intelligence and Prevention System
- **Track / Organization:** Great Indian AI Internship Challenge — Gnani AI
- **Problem Statement:** In India, financial fraud syndicates exploit phone calls to manipulate victims through psychological coercion—impersonating law enforcement (CBI "digital arrest"), threatening utility disconnection, and coercing victims into disclosing OTPs/verification codes or installing remote-access tools like AnyDesk. Non-tech-savvy citizens and elderly individuals need immediate, understandable, and evidence-based guidance in their native language before taking irreversible steps.
- **Solution:** VoiceShield AI is an explainable voice scam intelligence dashboard. It transcribes audio calls using Gnani Prisma STT, evaluates social engineering tactics sentence-by-sentence using a deterministic explainable RiskEngine, highlights verbatim evidence quotes, and speaks actionable safety advice in Indic languages using Gnani Timbre TTS.
- **Target Users:** General citizens, bank account holders, digital banking users, elderly family members, and consumer cyber-safety helpdesks.
- **Key Features:**
  - Multilingual support for Hindi (Devanagari), Hinglish (code-switched), and Indian English.
  - Sentence-by-sentence explainability: pins the exact excerpt and rationale instead of an opaque black-box score.
  - Contextual awareness: distinguishes between coercive credential requests and protective advice (e.g. *"Never share your OTP"*).
  - Spoken audio safety guidance using Gnani Timbre TTS.
  - Ephemeral processing with zero audio data retention and strict 20MB file upload protection.
  - Explicit Demo Mode to rehearse presentations without consuming API credits.
- **Technical Contribution:** A lightweight, explainable cybersecurity pipeline combining Indic speech AI with deterministic rule-based explainability that avoids the latency, cost, and hallucination risks of generative LLMs for critical security triage.

---

## Part B: Technical Architecture Explanation

VoiceShield AI uses a decoupled two-tier architecture:

1. **Frontend (Presentation Tier):**
   - Built with React 18, TypeScript, and Tailwind CSS using Vite.
   - Designed with a clean, dark-mode cybersecurity aesthetic.
   - Provides audio file upload with client-side 20MB validation, audio preview player, language selector, verbatim evidence viewer, and speech guidance player.
   - Features a visible **Demo Mode** indicator to ensure transparent demonstration.
   - Completely client-side secret-free: no API keys exist in frontend code.

2. **Backend (Application & Logic Tier):**
   - Built with Python 3.12 and FastAPI, running on Uvicorn.
   - `safe_read()` reads audio in 1MB chunks to enforce memory limits (HTTP 413) without persisting files to disk.
   - **GnaniSTTService:** Communicates with Gnani Prisma STT v3 (`https://api.vachana.ai/stt/v3`) using async HTTPX with 30s timeout and multipart form data.
   - **RiskEngine:** Deterministic, sentence-level analyzer matching named patterns (`OTP_REQUEST`, `PAYMENT_PRESSURE`, `IMPERSONATION`, `REMOTE_ACCESS`) while filtering out sentences with protective context (`PROTECTIVE_CONTEXT`).
   - **SafetyGuidanceService:** Translates risk indicators into actionable advice.
   - **GnaniTTSService:** Communicates with Gnani Timbre TTS v2.5 (`https://api.vachana.ai/api/v1/tts/inference`) using model `timbre-v2.5` to generate WAV audio.

3. **Data Flow:**
   `Audio File` ➔ `FastAPI Router` ➔ `Gnani Prisma STT` ➔ `Transcript` ➔ `RiskEngine` ➔ `Indicators & Severity` ➔ `SafetyGuidanceService` ➔ `Gnani Timbre TTS` ➔ `Frontend Dashboard`.

---

## Part C: Realistic 60–90 Second Demonstration Script

*(Total Duration: ~75 Seconds)*

### 1. Introduction (0:00 – 0:15)
- **Visual:** Display the VoiceShield AI dashboard (`http://localhost:5173`) in dark mode.
- **Speaker:** 
  > "Hello everyone. I am presenting VoiceShield AI—an explainable, multilingual voice scam intelligence system built for the Great Indian AI Internship Challenge organized by Gnani AI. Voice scam calls across India often coerce victims into revealing OTPs, installing remote-access tools, or transferring money under manufactured threats."

### 2. Suspicious Scam Example — OTP & Urgency (0:15 – 0:40)
- **Action:** Select **Auto Detect / Hinglish**, upload a sample recording (or use Demo Mode), and click **Analyze Audio**.
- **Visual:** Results appear showing **Verdict: HIGH RISK / SCAM DETECTED**.
- **Speaker:**
  > "Let's test a suspicious recording. The system ingests the audio and transcribes it using Gnani Prisma speech-to-text. Notice the verdict immediately flags HIGH RISK. But unlike a black-box model that just gives a percentage, VoiceShield explains why. Under Scam Indicators, it highlights the exact verbatim quote: *'Please share the OTP sent to your phone immediately to verify your account'*, and explains the exact manipulation tactic."

### 3. Safety Guidance & Spoken Audio (0:40 – 0:55)
- **Action:** Point to **Recommended Action** and click **Play Voice Advice**.
- **Visual:** Audio guidance waveform plays (or in Demo Mode, explains that live voice generation is available with configured credentials).
- **Speaker:**
  > "Under Recommended Action, VoiceShield gives clear advice: *'Never share your OTP or password. Hang up immediately and contact your institution directly.'* With Gnani Timbre TTS, this advice can be synthesized as spoken audio in the user's language, making protection accessible even for users who cannot read English."

### 4. Protective Advice & False Positive Rejection (0:55 – 1:10)
- **Action:** Demonstrate that benign educational or defensive guidance is not flagged.
- **Speaker:**
  > "Crucially, VoiceShield does not blindly match keywords. If a bank sends an educational advisory saying *'Never share your OTP with anyone'* or *'Beware of scammers impersonating police'*, our RiskEngine's contextual filter recognizes it as protective advice and rates it SAFE, avoiding false alarms."

### 5. Limitations & Closing (1:10 – 1:20)
- **Visual:** Show the clean report export via **Export JSON**.
- **Speaker:**
  > "VoiceShield uses deterministic pattern matching for zero-latency, explainable triage without hallucination. While it does not legally prove caller identity, it provides immediate evidence to protect victims before fraud occurs. Thank you!"

*(Note for Presenter: If presenting in Demo Mode without API credits, explicitly mention: "For this rehearsal, the application is running in VoiceShield's built-in Demo Mode, preserving API quota while demonstrating the full analysis workflow.")*

---

## Part D: Demo Recording Checklist

Follow this checklist before recording your demonstration video:

- [ ] **Browser Preparation:**
  - [ ] Open Chrome/Edge at `http://localhost:5173` in Full Screen or 1080p window.
  - [ ] Clear old files or errors by clicking **Reset**.
  - [ ] Ensure browser zoom is set to 100% or 110% for clear text readability.
  - [ ] Close all other tabs, bookmarks bar, and developer tools.
- [ ] **Credential & Privacy Check:**
  - [ ] Verify no `.env` files, API keys, or tokens are visible on screen or in terminal windows.
  - [ ] Ensure no personal WhatsApp/email notifications pop up during recording.
- [ ] **Sample Audio Preparation:**
  - [ ] Prepare 1 suspicious sample call recording (e.g. OTP demand or payment pressure) under 20MB in `.wav` or `.mp3`.
  - [ ] Verify audio plays clearly through system speakers.
- [ ] **Services Running:**
  - [ ] Backend running on PowerShell: `.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000`
  - [ ] Frontend running on PowerShell: `npm run dev`
  - [ ] Verify `http://localhost:8000/health` returns `{"status": "healthy"}`.
- [ ] **Recording Settings:**
  - [ ] Resolution: 1920x1080 (1080p) at 30 or 60 fps (OBS Studio or Windows Game Bar `Win + Alt + R`).
  - [ ] Microphone audio: clear, with background noise suppressed.
  - [ ] System audio enabled so TTS audio playback is captured in the recording.
- [ ] **Final Recording Review:**
  - [ ] Watch the recorded video from start to finish.
  - [ ] Confirm no credentials appear in any frame.
  - [ ] Confirm audio volume is balanced between your voice and the application sound.

---

## Part E: Submission Checklist

Before submitting to the Gnani AI Great Indian AI Internship Challenge, prepare and verify:

- [ ] **Public GitHub Repository:**
  - URL: `https://github.com/DivyanshuDubey10/VoiceShield-AI`
  - Repository set to **Public**.
  - `.env` file is NOT committed (verified by `.gitignore`).
  - README is up to date and contains setup instructions, architecture, and verification status.
- [ ] **Demonstration Video:**
  - Length: 60 to 90 seconds.
  - Demonstrates file upload, transcript analysis, scam indicators, safety guidance, and false positive avoidance.
  - Uploaded to YouTube (Unlisted or Public) or Google Drive (accessible to anyone with link).
- [ ] **Social Media Announcement Post (LinkedIn / X):**
  - Text template prepared (see below).
  - Tags Gnani AI.
  - Includes mandatory hashtags: `#GnaniAI` and `#GreatIndianAIInternshipChallenge`.
- [ ] **Short Project Pitch Text:**
  - "VoiceShield AI is an explainable voice scam prevention system for Indian phone calls. Using Gnani Prisma STT and Timbre TTS combined with a deterministic RiskEngine, it transcribes suspicious calls in Hindi, Hinglish, and English, highlights exact manipulation evidence, and delivers spoken safety warnings to prevent financial fraud before victims transfer money."

---

## Social Media Announcement Template (LinkedIn / X)

*(Copy and review before posting)*

```
🚀 Excited to share my submission for the Great Indian AI Internship Challenge organized by Gnani AI!

Introducing VoiceShield AI — a Multilingual Voice Scam Intelligence and Prevention System designed to safeguard citizens against phone scams across India.

📱 In a country where scammers impersonate authorities (CBI, police) or pressure victims into sharing OTPs and installing AnyDesk, victims need immediate, understandable protection.

VoiceShield AI solves this by:
🎙️ Transcribing suspicious calls in Hindi, Hinglish, and English using Gnani Prisma STT.
🔍 Analyzing social engineering manipulation sentence-by-sentence using an explainable Risk Engine that isolates exact evidence quotes.
🛡️ Filtering out false alarms from educational safety advisories.
🔊 Synthesizing actionable spoken guidance in Indian languages using Gnani Timbre TTS.

Check out the project:
GitHub: https://github.com/DivyanshuDubey10/VoiceShield-AI

#GnaniAI #GreatIndianAIInternshipChallenge #VoiceAI #CyberSecurity #ArtificialIntelligence #SpeechAI #IndianTech
```
