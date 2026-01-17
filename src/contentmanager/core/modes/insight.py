"""Insight Mode - Full synthesis pipeline for insight-driven content.

This mode provides high-level methods for generating content using the
complete synthesis pipeline with insight analysis, scenario generation,
and human voice transformation.
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.core.content.generator import ContentGenerator, GeneratedContent
from contentmanager.core.content.synthesis import SynthesisMode


@dataclass
class InsightModeResult:
    """Result from insight mode generation."""

    content: GeneratedContent
    insights_used: int
    synthesis_mode: str
    ai_score: float
    humanization_applied: bool


class InsightMode:
    """Mode for generating insight-driven synthesized content.

    This mode uses the full synthesis pipeline:
    - Insight extraction from document sections
    - Scenario context generation
    - Synthesis with various perspective modes
    - AI pattern detection and humanization
    """

    def __init__(
        self,
        session: AsyncSession,
        document_id: Optional[int] = None,
        default_synthesis_mode: str = "CHALLENGE",
        default_persona: str = "conversational",
        ai_threshold: float = 0.5,
    ):
        """Initialize insight mode.

        Args:
            session: Database session.
            document_id: Optional document ID to use.
            default_synthesis_mode: Default synthesis mode.
            default_persona: Default writing persona.
            ai_threshold: Maximum AI score threshold.
        """
        self.generator = ContentGenerator(
            session=session,
            document_id=document_id,
            default_synthesis_mode=default_synthesis_mode,
            default_persona=default_persona,
            ai_pattern_threshold=ai_threshold,
        )
        self.default_synthesis_mode = default_synthesis_mode
        self.default_persona = default_persona

    async def generate_insight_tweet(
        self,
        topic: str,
        section_nums: Optional[list[int]] = None,
        synthesis_mode: Optional[str] = None,
        persona: Optional[str] = None,
        use_scenario: bool = True,
    ) -> InsightModeResult:
        """Generate a tweet using full insight synthesis pipeline.

        Args:
            topic: Topic to generate content about.
            section_nums: Optional specific sections to focus on.
            synthesis_mode: Mode for synthesis (EXPLAIN, CONTRAST, CHALLENGE, etc.).
            persona: Writing persona to use.
            use_scenario: Whether to include scenario context.

        Returns:
            InsightModeResult with generated content and metadata.
        """
        mode = synthesis_mode or self.default_synthesis_mode
        persona_name = persona or self.default_persona

        content = await self.generator.generate_synthesized_tweet(
            topic=topic,
            mode="insight",
            section_nums=section_nums,
            synthesis_mode=mode,
            use_scenario=use_scenario,
            persona=persona_name,
        )

        return InsightModeResult(
            content=content,
            insights_used=len(content.citations) if content.citations else 0,
            synthesis_mode=mode,
            ai_score=content.ai_score or 0.0,
            humanization_applied=content.humanization_applied,
        )

    async def generate_perspective_thread(
        self,
        topic: str,
        perspective: str = "CHALLENGE",
        num_tweets: int = 5,
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
        use_scenario: bool = True,
    ) -> InsightModeResult:
        """Generate a thread from a specific perspective.

        Args:
            topic: Topic to generate content about.
            perspective: The perspective/synthesis mode to use.
            num_tweets: Number of tweets in thread.
            section_nums: Optional specific sections to focus on.
            persona: Writing persona to use.
            use_scenario: Whether to include scenario context.

        Returns:
            InsightModeResult with generated thread and metadata.
        """
        persona_name = persona or self.default_persona

        content = await self.generator.generate_synthesized_thread(
            topic=topic,
            num_tweets=num_tweets,
            mode="insight",
            section_nums=section_nums,
            synthesis_mode=perspective,
            use_scenario=use_scenario,
            persona=persona_name,
        )

        return InsightModeResult(
            content=content,
            insights_used=len(content.citations) if content.citations else 0,
            synthesis_mode=perspective,
            ai_score=content.ai_score or 0.0,
            humanization_applied=content.humanization_applied,
        )

    async def generate_explainer(
        self,
        topic: str,
        content_type: str = "tweet",
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
    ) -> InsightModeResult:
        """Generate explanatory content about a topic.

        Uses EXPLAIN synthesis mode for clear, accessible explanation.

        Args:
            topic: Topic to explain.
            content_type: "tweet" or "thread".
            section_nums: Optional specific sections.
            persona: Writing persona.

        Returns:
            InsightModeResult with explanatory content.
        """
        if content_type == "thread":
            return await self.generate_perspective_thread(
                topic=topic,
                perspective="EXPLAIN",
                num_tweets=5,
                section_nums=section_nums,
                persona=persona,
            )
        else:
            return await self.generate_insight_tweet(
                topic=topic,
                section_nums=section_nums,
                synthesis_mode="EXPLAIN",
                persona=persona,
            )

    async def generate_challenger(
        self,
        topic: str,
        content_type: str = "tweet",
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
    ) -> InsightModeResult:
        """Generate content that challenges assumptions.

        Uses CHALLENGE synthesis mode for provocative angles.

        Args:
            topic: Topic to challenge assumptions about.
            content_type: "tweet" or "thread".
            section_nums: Optional specific sections.
            persona: Writing persona.

        Returns:
            InsightModeResult with challenging content.
        """
        if content_type == "thread":
            return await self.generate_perspective_thread(
                topic=topic,
                perspective="CHALLENGE",
                num_tweets=5,
                section_nums=section_nums,
                persona=persona,
            )
        else:
            return await self.generate_insight_tweet(
                topic=topic,
                section_nums=section_nums,
                synthesis_mode="CHALLENGE",
                persona=persona,
            )

    async def generate_contrast(
        self,
        topic: str,
        content_type: str = "tweet",
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
    ) -> InsightModeResult:
        """Generate content contrasting expectation vs reality.

        Uses CONTRAST synthesis mode.

        Args:
            topic: Topic to contrast.
            content_type: "tweet" or "thread".
            section_nums: Optional specific sections.
            persona: Writing persona.

        Returns:
            InsightModeResult with contrast content.
        """
        if content_type == "thread":
            return await self.generate_perspective_thread(
                topic=topic,
                perspective="CONTRAST",
                num_tweets=5,
                section_nums=section_nums,
                persona=persona,
            )
        else:
            return await self.generate_insight_tweet(
                topic=topic,
                section_nums=section_nums,
                synthesis_mode="CONTRAST",
                persona=persona,
            )

    async def generate_story(
        self,
        topic: str,
        num_tweets: int = 5,
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
    ) -> InsightModeResult:
        """Generate narrative-style content.

        Uses STORY synthesis mode for narrative structure.

        Args:
            topic: Topic for the story.
            num_tweets: Number of tweets (for threads).
            section_nums: Optional specific sections.
            persona: Writing persona.

        Returns:
            InsightModeResult with story content.
        """
        return await self.generate_perspective_thread(
            topic=topic,
            perspective="STORY",
            num_tweets=num_tweets,
            section_nums=section_nums,
            persona=persona,
        )

    async def generate_application(
        self,
        topic: str,
        content_type: str = "tweet",
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
    ) -> InsightModeResult:
        """Generate content showing real-world application.

        Uses APPLY synthesis mode.

        Args:
            topic: Topic to show application of.
            content_type: "tweet" or "thread".
            section_nums: Optional specific sections.
            persona: Writing persona.

        Returns:
            InsightModeResult with application content.
        """
        if content_type == "thread":
            return await self.generate_perspective_thread(
                topic=topic,
                perspective="APPLY",
                num_tweets=5,
                section_nums=section_nums,
                persona=persona,
            )
        else:
            return await self.generate_insight_tweet(
                topic=topic,
                section_nums=section_nums,
                synthesis_mode="APPLY",
                persona=persona,
            )

    def get_available_perspectives(self) -> list[str]:
        """Get list of available synthesis perspectives."""
        return self.generator.get_available_synthesis_modes()

    def get_available_personas(self) -> list[str]:
        """Get list of available writing personas."""
        return self.generator.get_available_personas()
