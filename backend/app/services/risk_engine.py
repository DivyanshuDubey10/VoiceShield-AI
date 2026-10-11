import re
from typing import List
from app.schemas.responses import Evidence

class RiskEngine:
    """
    Explainable, multilingual rule-based detection engine for voice scam tactics.
    Supports English, Hindi (Devanagari), and Hinglish (Code-switched).
    """
    
    PATTERNS = {
        "OTP_REQUEST": {
            "action_regex": (
                r"(?i)(?:"
                r"(?:otp|o\s*t\s*p|one\s*time\s*password|pin|password|ओ\s*टी\s*पी|ओटीपी|पिन|पासवर्ड)\s*.*?"
                r"(?:tell|share|read|give|verify|batao|bataiye|de\s*do|dijiye|bhejo|bhej\s*do|बताइ[येए]|बताओ|दीजि[येए]|शेयर|भेज[ोए])"
                r"|"
                r"(?:tell|share|read|give|verify|batao|bataiye|de\s*do|dijiye|bhejo|bhej\s*do|बताइ[येए]|बताओ|दीजि[येए]|शेयर|भेज[ोए])\s*.*?"
                r"(?:otp|o\s*t\s*p|one\s*time\s*password|pin|password|ओ\s*टी\s*पी|ओटीपी|पिन|पासवर्ड)"
                r")"
            ),
            "severity": "HIGH",
            "rationale": "Explicit request to disclose a one-time password (OTP) or PIN."
        },
        "PAYMENT_PRESSURE": {
            "action_regex": (
                r"(?i)(?:"
                # Urgent financial demand (English & Hinglish)
                r"(?:transfer|send|pay|deposit|bhejo|daalo|jama|kat\s*rahe|kat\s*jayenge)\s+.*?"
                r"(?:money|funds|cash|amount|paise|rupaye|rupees|fine|penalty|bill)\s*.*?"
                r"(?:immediately|urgent|urgently|right\s*now|turant|jaldi|abhi|fauran)"
                r"|"
                r"(?:immediately|urgent|urgently|right\s*now|turant|jaldi|abhi|fauran)\s+.*?"
                r"(?:transfer|send|pay|deposit|bhejo|daalo|jama)\s*.*?"
                r"(?:money|funds|cash|amount|paise|rupaye|rupees|fine|penalty|bill)"
                r"|"
                # Urgent financial demand (Hindi Devanagari)
                r"(?:तुरंत|जल्दी|अभी|फ़ौरन)\s*.*?(?:पैसे|रुपये|रुपए|रकम|बिल|जुर्माना)\s*.*?(?:ट्रांसफर|भेजो|डालो|जमा|कट)"
                r"|"
                r"(?:पैसे|रुपये|रुपए|रकम)\s*.*?(?:तुरंत|जल्दी|अभी|फ़ौरन)\s*.*?(?:ट्रांसफर|भेजो|डालो|जमा|कट)"
                r"|"
                # False threat of immediate account or service disconnection
                r"(?:account|khata|खाता|card|service|electricity|bijli|बिजली)\s*.*?"
                r"(?:block|blocked|suspended|deactivated|closed|band|ब्लॉक|बंद)\s*.*?"
                r"(?:immediately|urgent|right\s*now|turant|jaldi|abhi|तुरंत|जल्दी|अभी)"
                r"|"
                r"(?:immediately|urgent|right\s*now|turant|jaldi|abhi|तुरंत|जल्दी|अभी)\s*.*?"
                r"(?:account|khata|खाता|card|service|electricity|bijli|बिजली)\s*.*?"
                r"(?:block|blocked|suspended|deactivated|closed|band|ब्लॉक|बंद)"
                r")"
            ),
            "severity": "HIGH",
            "rationale": "Creating false urgency or threatening account action to force payment."
        },
        "IMPERSONATION": {
            "action_regex": (
                r"(?i)(?:"
                # English: Calling from authority, claiming to be an officer or department
                r"\b(?:(?:i\s+am|this\s+is)\s+(?:calling\s+)?from|calling\s+from)\s*.*?\b(?:police|cbi|customs|fedex|rbi|bank|head\s*office|department|court|crime\s*branch)\b"
                r"|"
                r"\b(?:this\s+is|i\s+am)\b\s*.*?\b(?:cbi|police\s+officer|bank\s+manager|customs\s+officer|inspector|digital\s*arrest|crime\s*branch)\b"
                r"|"
                # Hindi / Hinglish: Authority + "se bol raha hoon" / "se call hai"
                r"(?:police|cbi|customs|rbi|bank|head\s*office|thana|police\s*station|crime\s*branch|पुलिस|सीबीआई|कस्टम्स|आरबीआई|बैंक|थाना)\s*.*?"
                r"(?:se\s+(?:bol\s+raha|call\s+hai|phone\s+hai|baat\s+kar|bol\s+rahe)|se\s+officer|officer\s+bol|से\s+(?:बोल\s+रहा|कॉल\s+है|फोन\s+है|बात\s+कर|बोल\s+रहे)|ऑफिसर|अधिकारी)"
                r")"
            ),
            "severity": "MEDIUM",
            "rationale": "Claiming authority from law enforcement or official institutions."
        },
        "REMOTE_ACCESS": {
            "action_regex": (
                r"(?i)(?:"
                r"(?:install|download|open|chalu\s*karo|डाऊनलोड|डाउनलोड|इनस्टॉल|खोलो|चालू)\s*.*?"
                r"(?:anydesk|teamviewer|quicksupport|ultraviewer|rustdesk|remote\s*access)"
                r"|"
                r"(?:anydesk|teamviewer|quicksupport|ultraviewer|rustdesk|remote\s*access)\s*.*?"
                r"(?:install|download|open|chalu|app|application|code|id|डाऊनलोड|डाउनलोड|इनस्टॉल|खोलो|चालू|ऐप)"
                r")"
            ),
            "severity": "HIGH",
            "rationale": "Requesting installation or use of remote access software."
        }
    }
    
    # Phrases indicating defensive guidance or educational discussions across English, Hindi, and Hinglish
    PROTECTIVE_CONTEXT = (
        r"(?i)(?:"
        r"\b(?:never|do\s+not|don't)\s+(?:share|give|tell|disclose|install|download)\b|"
        r"\b(?:will\s+never\s+ask|scammers|impersonate|warning|protect|beware|official\s+warning|advisory)\b|"
        r"\b(?:kisi\s+ko\s+mat\s+(?:dena|batao|share)|mat\s+(?:dena|batao|bhejo|share|karna)|savdhaan|satark)\b|"
        r"(?:कभी.*?मत|शेयर\s*मत|मत\s*(?:देना|बताओ|दीजिए|भेजो)|सावधान|सतर्क|बैंक\s*कभी\s*नहीं\s*मांगता)"
        r")"
    )

    def analyze_transcript(self, transcript: str) -> List[Evidence]:
        """
        Analyzes a transcript sentence-by-sentence to identify scam indicators.
        Filters out protective advice and educational discussions.
        """
        if not transcript or not transcript.strip():
            return []

        indicators: List[Evidence] = []
        # Split on sentence boundaries (. ! ? । or newlines)
        sentences = re.split(r'(?<=[.!?।])\s+|\n+', transcript)
        
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if not sentence_clean:
                continue
                
            # Skip sentences that contain protective or educational context
            if re.search(self.PROTECTIVE_CONTEXT, sentence_clean):
                continue
            
            for ind_type, rule in self.PATTERNS.items():
                if re.search(rule["action_regex"], sentence_clean):
                    indicators.append(
                        Evidence(
                            excerpt=sentence_clean,
                            rationale=rule["rationale"],
                            severity=rule["severity"],
                            indicator_type=ind_type
                        )
                    )
                    
        # Deduplicate indicators by category
        unique_indicators = {}
        for ind in indicators:
            if ind.indicator_type not in unique_indicators:
                unique_indicators[ind.indicator_type] = ind
                
        return list(unique_indicators.values())
        
    def calculate_risk_level(self, indicators: List[Evidence]) -> str:
        """
        Calculates aggregate risk level: HIGH if any critical indicators,
        CAUTION for suspicious authority claims, LOW otherwise.
        """
        if any(ind.severity == "HIGH" for ind in indicators):
            return "HIGH"
        if any(ind.severity == "MEDIUM" for ind in indicators):
            return "CAUTION"
        return "LOW"
