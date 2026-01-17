"""Content format handlers for different output types."""

import re
from dataclasses import dataclass, field
from typing import Optional

from contentmanager.config import get_settings


@dataclass
class Tweet:
    """A single tweet."""

    content: str
    hashtags: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Get the full tweet text."""
        return self.content

    @property
    def length(self) -> int:
        """Get the character length."""
        return len(self.content)

    @property
    def is_valid_length(self) -> bool:
        """Check if tweet is within character limit."""
        settings = get_settings()
        return self.length <= settings.max_tweet_length


@dataclass
class Thread:
    """A Twitter thread (multiple connected tweets)."""

    tweets: list[Tweet] = field(default_factory=list)
    topic: Optional[str] = None

    def add_tweet(self, content: str) -> None:
        """Add a tweet to the thread."""
        self.tweets.append(Tweet(content=content))

    @property
    def total_length(self) -> int:
        """Get total character count across all tweets."""
        return sum(t.length for t in self.tweets)

    @property
    def tweet_count(self) -> int:
        """Get number of tweets in thread."""
        return len(self.tweets)

    def format_for_display(self) -> str:
        """Format thread for display/preview."""
        lines = []
        for i, tweet in enumerate(self.tweets, 1):
            lines.append(f"[{i}/{len(self.tweets)}] {tweet.content}")
        return "\n\n".join(lines)

    def format_for_storage(self) -> str:
        """Format thread for database storage."""
        return "\n---TWEET---\n".join(t.content for t in self.tweets)

    @classmethod
    def from_storage(cls, stored_text: str, topic: Optional[str] = None) -> "Thread":
        """Recreate thread from stored format."""
        thread = cls(topic=topic)
        for tweet_text in stored_text.split("\n---TWEET---\n"):
            if tweet_text.strip():
                thread.add_tweet(tweet_text.strip())
        return thread


@dataclass
class Script:
    """Longer-form educational content."""

    title: str
    content: str
    sections: list[str] = field(default_factory=list)
    duration_estimate: Optional[str] = None  # e.g., "2-3 minutes"
    citations: list[str] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        """Get word count."""
        return len(self.content.split())


class ContentFormatter:
    """Format and parse generated content."""

    def __init__(self):
        self.settings = get_settings()

    def parse_tweet(self, raw_content: str) -> Tweet:
        """Parse raw generated content into a Tweet."""
        content = self._clean_content(raw_content)

        # Extract hashtags
        hashtags = re.findall(r"#\w+", content)

        # Extract citations (Section X patterns)
        citations = re.findall(r"Section\s+\d+(?:\(\d+\))?", content, re.IGNORECASE)

        return Tweet(
            content=content,
            hashtags=hashtags,
            citations=citations,
        )

    def parse_thread(self, raw_content: str, topic: Optional[str] = None) -> Thread:
        """Parse raw generated content into a Thread."""
        thread = Thread(topic=topic)

        # Try different parsing patterns
        # Pattern 1: TWEET 1: content
        pattern1 = re.findall(r"TWEET\s*\d+:\s*(.+?)(?=TWEET\s*\d+:|$)", raw_content, re.DOTALL | re.IGNORECASE)

        # Pattern 2: [1/N] content
        pattern2 = re.findall(r"\[\d+/\d+\]\s*(.+?)(?=\[\d+/\d+\]|$)", raw_content, re.DOTALL)

        # Pattern 3: Numbered list (1. content)
        pattern3 = re.findall(r"^\d+\.\s*(.+?)(?=^\d+\.|$)", raw_content, re.MULTILINE | re.DOTALL)

        # Use whichever pattern found content
        tweets_content = pattern1 or pattern2 or pattern3

        if tweets_content:
            for tweet_text in tweets_content:
                cleaned = self._clean_content(tweet_text)
                if cleaned:
                    thread.add_tweet(cleaned)
        else:
            # Fallback: split by double newlines or treat as single tweet
            parts = raw_content.split("\n\n")
            for part in parts:
                cleaned = self._clean_content(part)
                if cleaned and len(cleaned) > 20:  # Minimum viable tweet
                    thread.add_tweet(cleaned)

        return thread

    def parse_script(self, raw_content: str, title: str = "Untitled") -> Script:
        """Parse raw generated content into a Script."""
        content = self._clean_content(raw_content)

        # Extract sections (headers)
        sections = re.findall(r"^##?\s*(.+)$", content, re.MULTILINE)

        # Extract citations
        citations = re.findall(r"Section\s+\d+(?:\(\d+\))?", content, re.IGNORECASE)

        # Estimate duration (rough: 150 words per minute)
        word_count = len(content.split())
        minutes = word_count / 150
        if minutes < 1:
            duration = "Under 1 minute"
        elif minutes < 2:
            duration = "1-2 minutes"
        elif minutes < 5:
            duration = "2-5 minutes"
        else:
            duration = f"About {int(minutes)} minutes"

        return Script(
            title=title,
            content=content,
            sections=sections,
            duration_estimate=duration,
            citations=list(set(citations)),
        )

    def format_tweet_for_posting(self, tweet: Tweet) -> str:
        """Format a tweet for posting to Twitter."""
        content = tweet.content

        # Ensure it's within limits
        if len(content) > self.settings.max_tweet_length:
            # Truncate intelligently
            content = self._smart_truncate(content, self.settings.max_tweet_length - 3) + "..."

        return content

    def format_thread_for_posting(self, thread: Thread) -> list[str]:
        """Format a thread for posting to Twitter."""
        formatted = []
        for i, tweet in enumerate(thread.tweets):
            content = tweet.content

            # Add numbering if not present
            if not re.match(r"^\[\d+/\d+\]", content):
                prefix = f"[{i + 1}/{len(thread.tweets)}] "
                max_content_len = self.settings.max_tweet_length - len(prefix)
                if len(content) > max_content_len:
                    content = self._smart_truncate(content, max_content_len - 3) + "..."
                content = prefix + content

            # Ensure within limits
            if len(content) > self.settings.max_tweet_length:
                content = self._smart_truncate(content, self.settings.max_tweet_length - 3) + "..."

            formatted.append(content)

        return formatted

    def add_hashtags(self, content: str, hashtags: Optional[list[str]] = None) -> str:
        """Add hashtags to content if space allows."""
        if hashtags is None:
            hashtags = self.settings.default_hashtags

        # Check if hashtags are already present
        existing = set(re.findall(r"#\w+", content.lower()))

        # Add missing hashtags if space allows
        for tag in hashtags:
            tag_lower = tag.lower() if tag.startswith("#") else f"#{tag}".lower()
            if tag_lower not in existing:
                tag_to_add = tag if tag.startswith("#") else f"#{tag}"
                potential = f"{content} {tag_to_add}"
                if len(potential) <= self.settings.max_tweet_length:
                    content = potential
                    existing.add(tag_lower)

        return content

    def _clean_content(self, text: str) -> str:
        """Clean and normalize content."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Remove common artifacts
        text = re.sub(r"^(TWEET\s*\d+:|Reply:|Answer:)\s*", "", text, flags=re.IGNORECASE)
        return text

    def _smart_truncate(self, text: str, max_length: int) -> str:
        """Truncate text at a word boundary."""
        if len(text) <= max_length:
            return text

        truncated = text[:max_length]
        # Find last space
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.7:  # Don't truncate too much
            truncated = truncated[:last_space]

        return truncated.rstrip(".,!?;:-")
