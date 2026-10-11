# Architecture

```mermaid
graph TD
    User([User]) -->|Uploads Audio| Frontend(React + Vite)
    Frontend -->|POST /end-to-end| API(FastAPI Router)
    
    API -->|1. Multipart Audio| STT(GnaniSTTService)
    STT -->|POST| Prisma[Gnani Prisma API]
    Prisma -.->|Transcript| STT
    
    API -->|2. Transcript| RiskEngine(Risk Engine)
    RiskEngine -->|Rules / Regex| Detect[Indicator Detection]
    RiskEngine -->|Logic| Scorer[Risk Categorization]
    
    API -->|3. Risk & Indicators| Safety(SafetyGuidanceService)
    Safety -.->|Guidance Text| API
    
    API -->|4. Guidance Text| TTS(GnaniTTSService)
    TTS -->|POST| Timbre[Gnani Timbre API]
    Timbre -.->|Base64 Audio| TTS
    
    TTS -.->|Audio + Results| Frontend
    Frontend -->|Play/View| User
```

## Modules
1. **API Router**: Handles HTTP requests, validation, file size limits.
2. **GnaniSTTService**: Asynchronous HTTPX client for `api.vachana.ai/stt/v3`.
3. **RiskEngine**: Evaluates text against scam topologies (OTP requests, urgency).
4. **SafetyGuidanceService**: Generates context-specific warnings based on risk.
5. **GnaniTTSService**: Synthesizes warnings using `api.vachana.ai/api/v1/tts/inference`.
