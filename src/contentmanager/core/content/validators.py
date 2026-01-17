"""Content validation for generated content."""

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Tuple

from contentmanager.config import get_settings

if TYPE_CHECKING:
    from contentmanager.core.content.ai_pattern_filter import AIPatternFilter, AIPatternReport


@dataclass
class ValidationResult:
    """Result of content validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    ai_score: Optional[float] = None  # AI pattern score (0.0-1.0)
    ai_pattern_report: Optional["AIPatternReport"] = None

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def add_suggestion(self, message: str) -> None:
        """Add a suggestion."""
        self.suggestions.append(message)

    @property
    def is_human_like(self) -> bool:
        """Check if content passes human-likeness threshold."""
        if self.ai_score is None:
            return True  # No AI analysis performed
        return self.ai_score < 0.5


class ContentValidator:
    """Validate generated content before queuing/posting."""

    def __init__(
        self,
        section_label: str = "Section",
        section_range: Optional[Tuple[int, int]] = None,
        default_hashtags: Optional[list[str]] = None,
    ):
        self.settings = get_settings()

        # Configurable document metadata
        self.section_label = section_label
        self.valid_section_range = section_range or (1, 1000)  # Default wide range
        self.default_hashtags = default_hashtags or ["KnowYourRights"]

        # Sensitive keywords that may require extra review
        self.sensitive_keywords = [
            "death penalty", "capital punishment", "abortion", "euthanasia",
            "hate speech", "incitement", "terrorism", "treason",
            "state of emergency", "martial law",
        ]

        # Legal advice indicators
        self.legal_advice_phrases = [
            "you should sue", "you can claim", "file a lawsuit",
            "you have a case", "take them to court", "lawyer up",
            "you're entitled to", "you must demand",
            "i advise you to", "my advice is",
        ]

    def validate_tweet(self, content: str) -> ValidationResult:
        """Validate a single tweet."""
        result = ValidationResult(is_valid=True)

        # Check length
        if len(content) > self.settings.max_tweet_length:
            result.add_error(
                f"Tweet exceeds {self.settings.max_tweet_length} characters "
                f"(current: {len(content)})"
            )

        if len(content) < 20:
            result.add_error("Tweet is too short (minimum 20 characters)")

        # Check for citation
        if not self._has_citation(content):
            result.add_warning(f"Tweet does not contain a {self.section_label.lower()} citation")
            result.add_suggestion(f"Consider adding a reference like '{self.section_label} X'")

        # Check for valid citations
        citations = self._extract_citations(content)
        for citation in citations:
            if not self._is_valid_section_number(citation):
                result.add_error(f"Invalid section number: {citation}")

        # Check for legal advice language
        if self._contains_legal_advice(content):
            result.add_warning("Content may contain language that sounds like legal advice")
            result.add_suggestion("Consider rephrasing to be more educational")

        # Check for sensitive topics
        sensitive = self._check_sensitive_content(content)
        if sensitive:
            result.add_warning(f"Content touches on sensitive topic: {sensitive}")
            result.add_suggestion("Consider adding a disclaimer or softer framing")

        # Check for hashtags
        hashtags = re.findall(r"#\w+", content)
        if not hashtags:
            result.add_suggestion("Consider adding relevant hashtags for reach")
        elif len(hashtags) > 5:
            result.add_warning("Too many hashtags may reduce engagement")

        return result

    def validate_thread(self, tweets: list[str]) -> ValidationResult:
        """Validate a Twitter thread."""
        result = ValidationResult(is_valid=True)

        if len(tweets) < 2:
            result.add_error("Thread must have at least 2 tweets")

        if len(tweets) > self.settings.max_thread_tweets:
            result.add_warning(
                f"Thread has {len(tweets)} tweets, "
                f"consider keeping it under {self.settings.max_thread_tweets}"
            )

        # Validate each tweet
        has_citation = False
        for i, tweet in enumerate(tweets, 1):
            tweet_result = self.validate_tweet(tweet)
            if not tweet_result.is_valid:
                for error in tweet_result.errors:
                    result.add_error(f"Tweet {i}: {error}")

            if self._has_citation(tweet):
                has_citation = True

        # Thread should have at least one citation
        if not has_citation:
            result.add_warning(f"Thread contains no {self.section_label.lower()} citations")

        # Check for logical flow (basic check)
        if tweets and not any(
            word in tweets[0].lower()
            for word in ["thread", "let's", "today", "did you know", "here's"]
        ):
            result.add_suggestion("Consider starting with a hook like 'Thread:' or a question")

        return result

    def validate_reply(self, content: str, original_mention: str) -> ValidationResult:
        """Validate a reply to a mention."""
        result = self.validate_tweet(content)

        # Additional checks for replies
        if self._contains_legal_advice(content):
            result.add_error(
                "Reply appears to give specific legal advice. "
                "Please redirect to professional legal counsel."
            )

        # Check if reply addresses the mention topic
        # (Basic keyword overlap check)
        mention_words = set(original_mention.lower().split())
        reply_words = set(content.lower().split())
        overlap = mention_words & reply_words - {"the", "a", "is", "are", "to", "of", "and", "in"}

        if len(overlap) < 2 and len(mention_words) > 5:
            result.add_warning("Reply may not directly address the user's question")

        return result

    def _has_citation(self, content: str) -> bool:
        """Check if content contains a section citation."""
        pattern = rf"{re.escape(self.section_label)}\s+\d+"
        return bool(re.search(pattern, content, re.IGNORECASE))

    def _extract_citations(self, content: str) -> list[int]:
        """Extract section numbers from content."""
        pattern = rf"{re.escape(self.section_label)}\s+(\d+)"
        matches = re.findall(pattern, content, re.IGNORECASE)
        return [int(m) for m in matches]

    def _is_valid_section_number(self, section_num: int) -> bool:
        """Check if a section number is within valid range."""
        min_num, max_num = self.valid_section_range
        return min_num <= section_num <= max_num

    def _contains_legal_advice(self, content: str) -> bool:
        """Check if content contains legal advice language."""
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in self.legal_advice_phrases)

    def _check_sensitive_content(self, content: str) -> Optional[str]:
        """Check for sensitive topic keywords."""
        content_lower = content.lower()
        for keyword in self.sensitive_keywords:
            if keyword in content_lower:
                return keyword
        return None

    def suggest_improvements(self, content: str, content_type: str = "tweet") -> list[str]:
        """Suggest improvements for content."""
        suggestions = []

        # Length optimization
        if content_type == "tweet":
            remaining = self.settings.max_tweet_length - len(content)
            if remaining > 30:
                suggestions.append(
                    f"You have {remaining} characters remaining. "
                    "Consider adding more context or hashtags."
                )

        # Engagement suggestions
        if not any(char in content for char in "?!"):
            suggestions.append(
                "Consider adding a question or exclamation to boost engagement"
            )

        # Hashtag suggestions
        hashtags = re.findall(r"#\w+", content)
        if not hashtags:
            suggested_tags = " or ".join(f"#{tag}" for tag in self.default_hashtags[:2])
            suggestions.append(f"Add hashtags like {suggested_tags}")

        # Call to action
        cta_phrases = ["learn more", "what do you think", "share", "let us know"]
        if not any(phrase in content.lower() for phrase in cta_phrases):
            suggestions.append("Consider adding a call to action")

        return suggestions

    def validate_human_likeness(
        self,
        content: str,
        threshold: float = 0.5
    ) -> ValidationResult:
        """Validate content for human-likeness using AI pattern detection.

        Args:
            content: Content to validate.
            threshold: Maximum allowed AI score (0.0-1.0, default 0.5).

        Returns:
            ValidationResult with AI pattern analysis.
        """
        from contentmanager.core.content.ai_pattern_filter import AIPatternFilter

        result = ValidationResult(is_valid=True)
        filter_instance = AIPatternFilter()

        # Analyze content for AI patterns
        report = filter_instance.analyze(content)
        result.ai_score = report.ai_score
        result.ai_pattern_report = report

        # Check threshold
        if report.ai_score > threshold:
            result.add_warning(
                f"Content may appear AI-generated (score: {report.ai_score:.2f}, "
                f"threshold: {threshold})"
            )

        # Add cliche warnings
        cliche_patterns = [
            p for p in report.patterns
            if p.category.value in ("cliche_opener", "cliche_phrase")
        ]
        if cliche_patterns:
            for pattern in cliche_patterns[:3]:  # Limit to top 3
                result.add_warning(f"AI cliche detected: '{pattern.matched_text}'")

        # Add corporate speak warnings
        corporate_patterns = [
            p for p in report.patterns
            if p.category.value == "corporate_speak"
        ]
        if corporate_patterns:
            words = [p.matched_text for p in corporate_patterns[:3]]
            result.add_warning(f"Consider replacing: {', '.join(words)}")

        # Add suggestions from report
        for suggestion in report.suggestions:
            result.add_suggestion(suggestion)

        # Check sentence variance
        if report.sentence_variance < 0.3:
            result.add_suggestion(
                "Vary sentence lengths for a more natural reading flow"
            )

        return result

    def validate_with_ai_check(
        self,
        content: str,
        content_type: str = "tweet",
        ai_threshold: float = 0.5
    ) -> ValidationResult:
        """Combined validation: standard checks + AI pattern detection.

        Args:
            content: Content to validate.
            content_type: Type of content ("tweet", "thread", "reply").
            ai_threshold: Maximum allowed AI score.

        Returns:
            ValidationResult with both standard and AI pattern validation.
        """
        # Standard validation based on content type
        if content_type == "tweet":
            result = self.validate_tweet(content)
        elif content_type == "thread":
            # For single content string, validate as tweet
            result = self.validate_tweet(content)
        else:
            result = self.validate_tweet(content)

        # Add AI pattern validation
        ai_result = self.validate_human_likeness(content, ai_threshold)

        # Merge AI validation results
        result.ai_score = ai_result.ai_score
        result.ai_pattern_report = ai_result.ai_pattern_report

        for warning in ai_result.warnings:
            result.add_warning(warning)

        for suggestion in ai_result.suggestions:
            if suggestion not in result.suggestions:
                result.add_suggestion(suggestion)

        return result

    def get_ai_cliche_phrases(self) -> list[str]:
        """Get list of AI cliche phrases to avoid."""
        from contentmanager.core.content.ai_pattern_filter import AIPatternFilter

        return (
            AIPatternFilter.CLICHE_OPENERS +
            AIPatternFilter.CLICHE_PHRASES +
            AIPatternFilter.CORPORATE_SPEAK
        )
