# Synthetic Demo Audio Samples

This directory contains synthetic audio recordings generated using **Gnani Timbre TTS** for testing and demonstration purposes. No real personal phone recordings, victim data, or PII are used.

### Included Samples

1. **`sample_scam_otp_pressure.wav`**
   - **Content:** *"Hello, this is your bank security manager. We have detected suspicious transactions on your account. Please share your OTP immediately or your account will be blocked."*
   - **Expected Result:** `HIGH RISK` (detects `OTP_REQUEST` and `PAYMENT_PRESSURE`).

2. **`sample_scam_remote_access.wav`**
   - **Content:** *"I am calling from technical support. Your computer has a virus. Please install AnyDesk application immediately so I can fix your system."*
   - **Expected Result:** `HIGH RISK` (detects `REMOTE_ACCESS`).

3. **`sample_benign_protective_advisory.wav`**
   - **Content:** *"This is an official security advisory from your bank. Remember that our bank will never ask for your password or OTP. Never share your verification code with any caller."*
   - **Expected Result:** `SAFE / NO SCAM DETECTED` (contextual filter skips protective guidance to prevent false positives).
