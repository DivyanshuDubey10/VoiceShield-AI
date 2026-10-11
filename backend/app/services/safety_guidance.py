from typing import List
from app.schemas.responses import Evidence

def generate_safety_guidance(risk_level: str, indicators: List[Evidence]) -> str:
    """
    Generates actionable, plain-language guidance based on detected risk indicators.
    """
    if risk_level == "HIGH":
        guidance = "Warning. High-risk indicators detected. "
        if any(ind.indicator_type == "OTP_REQUEST" for ind in indicators):
            guidance += "Never share your OTP, PIN, or password with anyone, even if they claim to be from the bank. "
        if any(ind.indicator_type == "REMOTE_ACCESS" for ind in indicators):
            guidance += "Do not install any applications like AnyDesk or TeamViewer. "
        
        guidance += "Hang up immediately and contact your institution directly using their official verified phone number."
        return guidance
        
    elif risk_level == "CAUTION":
        return "Exercise caution. Verify the caller's identity independently before taking any action. Do not share sensitive details."
        
    else:
        return "No obvious high-risk indicators were detected. However, remain vigilant and never share passwords or OTPs."

class SafetyGuidanceService:
    """Service wrapper for backward-compatibility with existing router."""
    def generate_guidance(self, risk_level: str, indicators: List[Evidence]) -> str:
        return generate_safety_guidance(risk_level, indicators)
