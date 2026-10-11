# Project Pitch

**Title:** VoiceShield AI: Explainable Multilingual Voice Scam Intelligence

**Problem:** Scammers are using voice calls to manipulate victims into sharing OTPs or transferring funds. Victims need immediate, understandable, and evidence-based guidance in their native language to prevent fraud.

**Solution:** VoiceShield AI is a dashboard that analyzes suspicious call recordings. It uses Gnani Prisma to transcribe the call and a custom detection engine to pinpoint exact social engineering indicators (like false urgency or OTP requests). It then explains the risk and plays actionable safety guidance using Gnani Timbre, ensuring the user is protected before taking irreversible actions.

**Why it matters:** By focusing on explainability rather than just an opaque "risk score," users understand exactly *why* a call is dangerous, educating them for the future.

---

# 60-Second Demo Script

*(Show the dashboard with dark mode UI)*
"Hello, I'm excited to present VoiceShield AI. Let's say you receive a suspicious voicemail claiming your bank account is blocked."

*(Click 'Upload' and select audio, hit Analyze)*
"We upload the audio. The backend sends this to Gnani Prisma for real-time transcription."

*(Screen shows transcript appearing)*
"VoiceShield's detection engine analyzes the text. Notice how it flags specific sentences—here, the caller creating false urgency, and here, asking for an OTP."

*(Screen shows Risk Assessment: HIGH)*
"Instead of just saying 'Fraud', it provides exact evidence from the transcript so the user understands the manipulation tactics."

*(Click 'Listen to Guidance')*
"Finally, we use Gnani Timbre to generate a spoken warning in the user's language, making the guidance accessible."
*(Audio plays: "Warning. High-risk indicators detected. Never share your OTP...")*

"VoiceShield AI: Explainable, measurable, and safe. Thank you."
