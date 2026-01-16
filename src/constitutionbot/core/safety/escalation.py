"""Escalation handling for sensitive queries."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EscalationType(str, Enum):
    """Types of escalation needed."""

    NONE = "none"
    LEGAL_REFERRAL = "legal_referral"
    EMERGENCY = "emergency"
    PROFESSIONAL_HELP = "professional_help"
    ADMIN_REVIEW = "admin_review"


@dataclass
class EscalationResult:
    """Result of escalation check."""

    escalation_type: EscalationType
    reason: Optional[str] = None
    suggested_response: Optional[str] = None
    referral_info: Optional[str] = None

    @property
    def needs_escalation(self) -> bool:
        return self.escalation_type != EscalationType.NONE


class EscalationHandler:
    """Handle escalation of sensitive queries to appropriate resources."""

    # Patterns indicating need for legal referral
    LEGAL_REFERRAL_PATTERNS = [
        r"\b(my|i|we)\s+(rights?\s+)?(were?|have\s+been)\s+(violated|infringed)\b",
        r"\b(sue|lawsuit|legal\s+action|claim|compensation)\b",
        r"\b(arrested|detained|charged|accused)\b",
        r"\b(lawyer|attorney|legal\s+aid|advocate)\b",
        r"\b(court\s+case|tribunal|legal\s+proceedings)\b",
        r"\bwhat\s+can\s+i\s+do\s+(about|if)\b",
        r"\bcan\s+i\s+(sue|claim|take\s+.+\s+to\s+court)\b",
    ]

    # Patterns indicating emergency
    EMERGENCY_PATTERNS = [
        r"\b(emergency|urgent|help\s+me|danger)\b",
        r"\b(violence|assault|abuse|threat)\s+(against|towards|to)\s+me\b",
        r"\b(being\s+held|kidnapped|detained\s+illegally)\b",
        r"\b(immediate|right\s+now|currently)\s+(danger|threat)\b",
    ]

    # Patterns indicating mental health concerns
    CRISIS_PATTERNS = [
        r"\b(suicide|kill\s+myself|end\s+my\s+life)\b",
        r"\b(hopeless|no\s+point|give\s+up)\b",
        r"\b(self[- ]harm|hurt\s+myself)\b",
    ]

    # Referral resources
    LEGAL_RESOURCES = """
For legal assistance in South Africa:
• Legal Aid SA: 0800 110 110 (toll-free)
• Lawyers for Human Rights: 012 320 2943
• Legal Resources Centre: 011 836 9831
• Your nearest Community Law Centre

This is general information, not legal advice.
"""

    EMERGENCY_RESOURCES = """
Emergency contacts:
• Police: 10111
• Ambulance: 10177
• Gender-Based Violence: 0800 428 428
• Human Rights Commission: 011 877 3600

If you're in immediate danger, please contact emergency services.
"""

    CRISIS_RESOURCES = """
If you're struggling, please reach out:
• SADAG 24hr helpline: 0800 567 567
• Lifeline: 0861 322 322
• Suicide Crisis Line: 0800 567 567

You don't have to face this alone.
"""

    def check_escalation(self, content: str) -> EscalationResult:
        """Check if content requires escalation."""
        content_lower = content.lower()

        # Check for crisis situations first (highest priority)
        for pattern in self.CRISIS_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return EscalationResult(
                    escalation_type=EscalationType.PROFESSIONAL_HELP,
                    reason="Mental health crisis indicators detected",
                    suggested_response=self._generate_crisis_response(),
                    referral_info=self.CRISIS_RESOURCES,
                )

        # Check for emergency situations
        for pattern in self.EMERGENCY_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return EscalationResult(
                    escalation_type=EscalationType.EMERGENCY,
                    reason="Emergency situation indicators detected",
                    suggested_response=self._generate_emergency_response(),
                    referral_info=self.EMERGENCY_RESOURCES,
                )

        # Check for legal referral needs
        for pattern in self.LEGAL_REFERRAL_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return EscalationResult(
                    escalation_type=EscalationType.LEGAL_REFERRAL,
                    reason="User appears to need specific legal advice",
                    suggested_response=self._generate_legal_referral_response(content),
                    referral_info=self.LEGAL_RESOURCES,
                )

        return EscalationResult(escalation_type=EscalationType.NONE)

    def _generate_crisis_response(self) -> str:
        """Generate response for mental health crisis."""
        return (
            "I'm concerned about what you've shared. While I can help with "
            "constitutional education, please reach out to a crisis helpline: "
            "SADAG 0800 567 567 (24hr). You matter, and help is available. 💙"
        )

    def _generate_emergency_response(self) -> str:
        """Generate response for emergency situations."""
        return (
            "This sounds urgent. If you're in immediate danger, please contact "
            "Police: 10111 or Ambulance: 10177. For rights violations, contact "
            "the Human Rights Commission: 011 877 3600. Stay safe. 🙏"
        )

    def _generate_legal_referral_response(self, context: str) -> str:
        """Generate response for legal referral."""
        return (
            "Thank you for your question. While I provide constitutional education, "
            "I can't give specific legal advice for your situation. For personalized "
            "legal help, please contact Legal Aid SA: 0800 110 110 (free) or visit "
            "your nearest legal aid clinic. #KnowYourRights"
        )

    def get_admin_alert(self, result: EscalationResult) -> Optional[str]:
        """Generate an alert for admin review."""
        if not result.needs_escalation:
            return None

        return f"""
⚠️ ESCALATION ALERT

Type: {result.escalation_type.value.upper()}
Reason: {result.reason}

Suggested Response:
{result.suggested_response}

Referral Resources:
{result.referral_info}

Please review and respond appropriately.
"""
