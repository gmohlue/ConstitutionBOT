"""Disclaimer management for content."""

from enum import Enum
from typing import Optional


class DisclaimerType(str, Enum):
    """Types of disclaimers."""

    GENERAL = "general"
    LEGAL = "legal"
    SENSITIVE = "sensitive"
    HISTORICAL = "historical"
    EDUCATIONAL = "educational"


class DisclaimerManager:
    """Manage disclaimers for different content types."""

    # Standard disclaimers
    DISCLAIMERS = {
        DisclaimerType.GENERAL: (
            "📚 This is educational content about the SA Constitution, not legal advice."
        ),
        DisclaimerType.LEGAL: (
            "⚖️ This is general information only. For specific legal advice, "
            "please consult a qualified legal professional."
        ),
        DisclaimerType.SENSITIVE: (
            "⚠️ This content discusses sensitive topics. "
            "Please engage respectfully and seek professional guidance if needed."
        ),
        DisclaimerType.HISTORICAL: (
            "📜 This content discusses historical events. "
            "The Constitution has evolved to address past injustices."
        ),
        DisclaimerType.EDUCATIONAL: (
            "🎓 Educational content for civic awareness. "
            "For detailed legal interpretation, consult legal resources."
        ),
    }

    # Short disclaimers for space-constrained contexts (tweets)
    SHORT_DISCLAIMERS = {
        DisclaimerType.GENERAL: "📚 Educational only, not legal advice.",
        DisclaimerType.LEGAL: "⚖️ General info only. Consult a lawyer for advice.",
        DisclaimerType.SENSITIVE: "⚠️ Sensitive topic. Seek guidance if needed.",
        DisclaimerType.HISTORICAL: "📜 Historical context. Constitution has evolved.",
        DisclaimerType.EDUCATIONAL: "🎓 For awareness. Consult legal resources.",
    }

    # Topics that trigger specific disclaimers
    TOPIC_DISCLAIMERS = {
        # Legal topics
        "rights violation": DisclaimerType.LEGAL,
        "sue": DisclaimerType.LEGAL,
        "court": DisclaimerType.LEGAL,
        "arrested": DisclaimerType.LEGAL,
        "detained": DisclaimerType.LEGAL,
        "lawyer": DisclaimerType.LEGAL,
        # Sensitive topics
        "death penalty": DisclaimerType.SENSITIVE,
        "abortion": DisclaimerType.SENSITIVE,
        "hate speech": DisclaimerType.SENSITIVE,
        "discrimination": DisclaimerType.SENSITIVE,
        "violence": DisclaimerType.SENSITIVE,
        # Historical topics
        "apartheid": DisclaimerType.HISTORICAL,
        "1994": DisclaimerType.HISTORICAL,
        "freedom day": DisclaimerType.HISTORICAL,
        "mandela": DisclaimerType.HISTORICAL,
        "reconciliation": DisclaimerType.HISTORICAL,
    }

    def get_disclaimer(
        self,
        disclaimer_type: DisclaimerType,
        short: bool = False,
    ) -> str:
        """Get a disclaimer by type."""
        if short:
            return self.SHORT_DISCLAIMERS.get(
                disclaimer_type,
                self.SHORT_DISCLAIMERS[DisclaimerType.GENERAL],
            )
        return self.DISCLAIMERS.get(
            disclaimer_type,
            self.DISCLAIMERS[DisclaimerType.GENERAL],
        )

    def detect_needed_disclaimer(self, content: str) -> Optional[DisclaimerType]:
        """Detect what type of disclaimer is needed based on content."""
        content_lower = content.lower()

        for keyword, disclaimer_type in self.TOPIC_DISCLAIMERS.items():
            if keyword in content_lower:
                return disclaimer_type

        return None

    def add_disclaimer_if_needed(
        self,
        content: str,
        max_length: Optional[int] = None,
        force_type: Optional[DisclaimerType] = None,
    ) -> str:
        """Add a disclaimer to content if needed and space allows."""
        # Determine disclaimer type
        disclaimer_type = force_type or self.detect_needed_disclaimer(content)

        if not disclaimer_type:
            return content

        # Get appropriate disclaimer
        if max_length:
            disclaimer = self.get_disclaimer(disclaimer_type, short=True)
            # Check if adding disclaimer would exceed limit
            if len(content) + len(disclaimer) + 2 > max_length:
                return content
        else:
            disclaimer = self.get_disclaimer(disclaimer_type, short=False)

        # Determine placement (at end for tweets, could be at start for threads)
        return f"{content}\n\n{disclaimer}"

    def add_thread_disclaimer(
        self,
        tweets: list[str],
        disclaimer_type: Optional[DisclaimerType] = None,
    ) -> list[str]:
        """Add disclaimer to a thread (typically at the end)."""
        if not tweets:
            return tweets

        # Detect needed disclaimer from thread content
        if not disclaimer_type:
            full_content = " ".join(tweets)
            disclaimer_type = self.detect_needed_disclaimer(full_content)

        if not disclaimer_type:
            disclaimer_type = DisclaimerType.EDUCATIONAL

        disclaimer = self.get_disclaimer(disclaimer_type, short=True)

        # Add to last tweet if space allows, otherwise add new tweet
        last_tweet = tweets[-1]
        if len(last_tweet) + len(disclaimer) + 2 <= 280:
            tweets[-1] = f"{last_tweet}\n\n{disclaimer}"
        else:
            # Add as final tweet
            tweets.append(disclaimer)

        return tweets

    def get_reply_disclaimer(self, original_content: str) -> Optional[str]:
        """Get an appropriate disclaimer for a reply based on the original content."""
        disclaimer_type = self.detect_needed_disclaimer(original_content)

        if disclaimer_type in (DisclaimerType.LEGAL, DisclaimerType.SENSITIVE):
            return self.get_disclaimer(disclaimer_type, short=True)

        return None
