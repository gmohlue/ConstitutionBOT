"""Content safety filters."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SafetyLevel(str, Enum):
    """Safety concern levels."""

    SAFE = "safe"
    CAUTION = "caution"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"


@dataclass
class SafetyResult:
    """Result of safety filtering."""

    level: SafetyLevel
    concerns: list[str] = field(default_factory=list)
    modifications: list[str] = field(default_factory=list)
    blocked_reason: Optional[str] = None

    @property
    def is_safe(self) -> bool:
        return self.level == SafetyLevel.SAFE

    @property
    def needs_review(self) -> bool:
        return self.level in (SafetyLevel.CAUTION, SafetyLevel.REVIEW_REQUIRED)

    @property
    def is_blocked(self) -> bool:
        return self.level == SafetyLevel.BLOCKED


class ContentFilter:
    """Filter content for safety and appropriateness."""

    # Blocked content patterns - never allow
    BLOCKED_PATTERNS = [
        r"\bkill\s+(all|them|the)\b",
        r"\bviolence\s+against\b",
        r"\bhate\s+(all|those)\b",
        r"\bexterminate\b",
        r"\bgenocide\b",
    ]

    # Profanity word list (common English profanity)
    PROFANITY_WORDS = {
        # Mild profanity - caution level
        "mild": [
            "damn", "dammit", "hell", "crap", "ass", "piss",
            "bloody", "bugger", "bollocks", "git", "sod",
        ],
        # Strong profanity - review required
        "strong": [
            "shit", "fuck", "fucking", "fucker", "fucked",
            "bitch", "bastard", "asshole", "dickhead", "prick",
            "cock", "cunt", "twat", "wanker", "bullshit",
        ],
        # Slurs - blocked (racial, ethnic, homophobic)
        "slurs": [
            "kaffir", "kaffer", "hotnot", "coolie", "boesman",
            "nigger", "nigga", "faggot", "fag", "dyke", "tranny",
            "retard", "spastic", "mong",
        ],
    }

    # Derogatory terms specific to South African context
    SA_SENSITIVE_TERMS = [
        "makwerekwere", "amakwerekwere",  # xenophobic term
        "swartgevaar",  # apartheid-era fear term
        "rooi gevaar",  # apartheid-era term
    ]

    # Sensitive topics requiring review
    SENSITIVE_TOPICS = {
        "death_penalty": ["death penalty", "capital punishment", "execution"],
        "abortion": ["abortion", "termination of pregnancy"],
        "euthanasia": ["euthanasia", "assisted suicide", "right to die"],
        "hate_speech": ["hate speech", "racial slurs", "ethnic slurs"],
        "violence": ["violence", "assault", "attack"],
        "terrorism": ["terrorism", "terrorist", "bomb", "attack"],
        "political": ["anc", "da", "eff", "political party", "elections", "vote for"],
    }

    # Legal advice indicators
    LEGAL_ADVICE_PATTERNS = [
        r"\byou\s+should\s+(sue|file|claim|demand)\b",
        r"\byou\s+have\s+a\s+case\b",
        r"\btake\s+(them|it)\s+to\s+court\b",
        r"\byou're\s+entitled\s+to\b",
        r"\byou\s+can\s+sue\b",
        r"\bi\s+advise\s+you\s+to\b",
        r"\bseek\s+damages\b",
    ]

    # Misinformation patterns
    MISINFORMATION_PATTERNS = [
        r"\bconstitution\s+(says|allows|permits)\s+.{0,20}(violence|discrimination)\b",
        r"\bno\s+rights\s+(for|to)\b",
        r"\bconstitution\s+is\s+(invalid|illegal|fake)\b",
    ]

    def filter(self, content: str) -> SafetyResult:
        """Run all safety filters on content."""
        result = SafetyResult(level=SafetyLevel.SAFE)
        content_lower = content.lower()

        # Check blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                result.level = SafetyLevel.BLOCKED
                result.blocked_reason = "Content contains prohibited language"
                return result

        # Check misinformation
        for pattern in self.MISINFORMATION_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                result.level = SafetyLevel.BLOCKED
                result.blocked_reason = "Content may contain constitutional misinformation"
                return result

        # Check legal advice
        for pattern in self.LEGAL_ADVICE_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                result.level = SafetyLevel.REVIEW_REQUIRED
                result.concerns.append("Content appears to provide specific legal advice")

        # Check profanity
        profanity_result = self._check_profanity(content_lower)
        if profanity_result["slurs"]:
            result.level = SafetyLevel.BLOCKED
            result.blocked_reason = "Content contains slurs or hate speech"
            return result
        if profanity_result["strong"]:
            result.level = SafetyLevel.REVIEW_REQUIRED
            result.concerns.append(f"Contains strong profanity: {', '.join(profanity_result['strong'][:3])}")
        if profanity_result["mild"]:
            if result.level == SafetyLevel.SAFE:
                result.level = SafetyLevel.CAUTION
            result.concerns.append(f"Contains mild profanity: {', '.join(profanity_result['mild'][:3])}")

        # Check SA-specific sensitive terms
        for term in self.SA_SENSITIVE_TERMS:
            if term in content_lower:
                result.level = SafetyLevel.BLOCKED
                result.blocked_reason = "Content contains derogatory or xenophobic terms"
                return result

        # Check sensitive topics
        for topic, keywords in self.SENSITIVE_TOPICS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    if result.level == SafetyLevel.SAFE:
                        result.level = SafetyLevel.CAUTION
                    result.concerns.append(f"Touches on sensitive topic: {topic}")
                    break

        # Check for potential bias/political content
        if self._check_political_bias(content_lower):
            if result.level == SafetyLevel.SAFE:
                result.level = SafetyLevel.CAUTION
            result.concerns.append("Content may have political implications")

        return result

    def filter_reply(self, reply: str, original_mention: str) -> SafetyResult:
        """Filter a reply with additional context."""
        result = self.filter(reply)

        # Additional checks for replies
        original_lower = original_mention.lower()

        # Check if responding to potentially harmful request
        harmful_request_indicators = [
            "how to break", "how to avoid", "loophole",
            "get around", "circumvent", "ignore the law",
        ]
        for indicator in harmful_request_indicators:
            if indicator in original_lower:
                if result.level == SafetyLevel.SAFE:
                    result.level = SafetyLevel.CAUTION
                result.concerns.append("Original mention may be requesting harmful information")

        return result

    def _check_political_bias(self, content: str) -> bool:
        """Check for potential political bias."""
        # Political party mentions
        parties = ["anc", "da", "eff", "ifp", "cope", "mk party"]
        for party in parties:
            if f" {party} " in f" {content} ":
                return True

        # Political figures (generic check)
        political_terms = [
            "president ramaphosa", "president zuma",
            "ruling party", "opposition",
        ]
        return any(term in content for term in political_terms)

    def _check_profanity(self, content: str) -> dict[str, list[str]]:
        """Check content for profanity words.

        Returns dict with lists of found words by severity level.
        """
        result = {"mild": [], "strong": [], "slurs": []}
        words = re.findall(r'\b\w+\b', content.lower())
        word_set = set(words)

        for level, word_list in self.PROFANITY_WORDS.items():
            for word in word_list:
                if word in word_set:
                    result[level].append(word)

        return result

    def sanitize(self, content: str) -> str:
        """Sanitize content by removing problematic elements."""
        # Remove potential HTML/script injection
        content = re.sub(r"<[^>]+>", "", content)

        # Remove URLs (optional, depending on policy)
        # content = re.sub(r'https?://\S+', '[link removed]', content)

        # Normalize whitespace
        content = re.sub(r"\s+", " ", content).strip()

        return content

    def get_moderation_notes(self, result: SafetyResult) -> str:
        """Generate moderation notes for a safety result."""
        if result.is_safe:
            return "Content passed all safety checks."

        notes = []

        if result.is_blocked:
            notes.append(f"BLOCKED: {result.blocked_reason}")
        elif result.level == SafetyLevel.REVIEW_REQUIRED:
            notes.append("REQUIRES REVIEW before posting")
        else:
            notes.append("CAUTION: Review recommended")

        if result.concerns:
            notes.append("Concerns:")
            for concern in result.concerns:
                notes.append(f"  - {concern}")

        if result.modifications:
            notes.append("Modifications made:")
            for mod in result.modifications:
                notes.append(f"  - {mod}")

        return "\n".join(notes)
