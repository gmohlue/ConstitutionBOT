"""Commentary Mode - Analytical commentary and myth-busting content.

This mode provides specialized methods for generating analytical content,
myth-busting pieces, and implications exploration using the synthesis pipeline.
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.core.content.generator import ContentGenerator, GeneratedContent
from contentmanager.core.content.insight_analyzer import InsightAnalyzer
from contentmanager.core.content.synthesis import SynthesisMode


@dataclass
class CommentaryResult:
    """Result from commentary mode generation."""

    content: GeneratedContent
    commentary_type: str  # analysis, myth_bust, implications
    sections_analyzed: int
    ai_score: float
    humanization_applied: bool


class CommentaryMode:
    """Mode for generating analytical commentary content.

    Specialized methods for:
    - In-depth analysis
    - Myth-busting content
    - Implications exploration
    - Critical perspectives
    """

    def __init__(
        self,
        session: AsyncSession,
        document_id: Optional[int] = None,
        default_persona: str = "thoughtful",
        ai_threshold: float = 0.5,
    ):
        """Initialize commentary mode.

        Args:
            session: Database session.
            document_id: Optional document ID.
            default_persona: Default writing persona (thoughtful works well for analysis).
            ai_threshold: Maximum AI score threshold.
        """
        self.generator = ContentGenerator(
            session=session,
            document_id=document_id,
            default_synthesis_mode="CHALLENGE",  # Commentary tends to be analytical
            default_persona=default_persona,
            ai_pattern_threshold=ai_threshold,
        )
        self.insight_analyzer = InsightAnalyzer()
        self.default_persona = default_persona

    async def generate_analysis(
        self,
        topic: str,
        content_type: str = "thread",
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
        depth: str = "standard",  # standard, deep
    ) -> CommentaryResult:
        """Generate analytical commentary on a topic.

        Creates content that analyzes a topic from multiple angles,
        exploring tensions, implications, and nuances.

        Args:
            topic: Topic to analyze.
            content_type: "tweet" or "thread".
            section_nums: Optional specific sections.
            persona: Writing persona (thoughtful recommended).
            depth: Analysis depth - "standard" or "deep".

        Returns:
            CommentaryResult with analytical content.
        """
        persona_name = persona or self.default_persona
        num_tweets = 7 if depth == "deep" else 5

        if content_type == "thread":
            content = await self.generator.generate_synthesized_thread(
                topic=topic,
                num_tweets=num_tweets,
                mode="commentary",
                section_nums=section_nums,
                synthesis_mode="IMPLICATIONS",
                use_scenario=True,
                persona=persona_name,
            )
        else:
            content = await self.generator.generate_synthesized_tweet(
                topic=topic,
                mode="commentary",
                section_nums=section_nums,
                synthesis_mode="IMPLICATIONS",
                use_scenario=True,
                persona=persona_name,
            )

        return CommentaryResult(
            content=content,
            commentary_type="analysis",
            sections_analyzed=len(content.citations) if content.citations else 0,
            ai_score=content.ai_score or 0.0,
            humanization_applied=content.humanization_applied,
        )

    async def generate_myth_buster(
        self,
        topic: str,
        content_type: str = "thread",
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
    ) -> CommentaryResult:
        """Generate content that debunks common myths.

        Creates content specifically designed to identify and
        address common misconceptions about a topic.

        Args:
            topic: Topic to bust myths about.
            content_type: "tweet" or "thread".
            section_nums: Optional specific sections.
            persona: Writing persona.

        Returns:
            CommentaryResult with myth-busting content.
        """
        persona_name = persona or self.default_persona

        if content_type == "thread":
            content = await self.generator.generate_synthesized_thread(
                topic=topic,
                num_tweets=5,
                mode="commentary",
                section_nums=section_nums,
                synthesis_mode="MYTH_BUST",
                use_scenario=False,  # Myths don't need scenario context
                persona=persona_name,
            )
        else:
            content = await self.generator.generate_synthesized_tweet(
                topic=topic,
                mode="commentary",
                section_nums=section_nums,
                synthesis_mode="MYTH_BUST",
                use_scenario=False,
                persona=persona_name,
            )

        return CommentaryResult(
            content=content,
            commentary_type="myth_bust",
            sections_analyzed=len(content.citations) if content.citations else 0,
            ai_score=content.ai_score or 0.0,
            humanization_applied=content.humanization_applied,
        )

    async def generate_implications(
        self,
        topic: str,
        content_type: str = "thread",
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
    ) -> CommentaryResult:
        """Generate content exploring real-world implications.

        Focuses on the ripple effects and practical consequences
        of a provision or concept.

        Args:
            topic: Topic to explore implications of.
            content_type: "tweet" or "thread".
            section_nums: Optional specific sections.
            persona: Writing persona.

        Returns:
            CommentaryResult with implications content.
        """
        persona_name = persona or self.default_persona

        if content_type == "thread":
            content = await self.generator.generate_synthesized_thread(
                topic=topic,
                num_tweets=5,
                mode="commentary",
                section_nums=section_nums,
                synthesis_mode="IMPLICATIONS",
                use_scenario=True,
                persona=persona_name,
            )
        else:
            content = await self.generator.generate_synthesized_tweet(
                topic=topic,
                mode="commentary",
                section_nums=section_nums,
                synthesis_mode="IMPLICATIONS",
                use_scenario=True,
                persona=persona_name,
            )

        return CommentaryResult(
            content=content,
            commentary_type="implications",
            sections_analyzed=len(content.citations) if content.citations else 0,
            ai_score=content.ai_score or 0.0,
            humanization_applied=content.humanization_applied,
        )

    async def generate_critical_perspective(
        self,
        topic: str,
        content_type: str = "thread",
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
    ) -> CommentaryResult:
        """Generate content with critical perspective.

        Creates content that examines tensions, trade-offs,
        and difficult questions about a topic.

        Args:
            topic: Topic to critically examine.
            content_type: "tweet" or "thread".
            section_nums: Optional specific sections.
            persona: Writing persona.

        Returns:
            CommentaryResult with critical perspective content.
        """
        persona_name = persona or self.default_persona

        if content_type == "thread":
            content = await self.generator.generate_synthesized_thread(
                topic=topic,
                num_tweets=5,
                mode="commentary",
                section_nums=section_nums,
                synthesis_mode="CHALLENGE",
                use_scenario=True,
                persona=persona_name,
            )
        else:
            content = await self.generator.generate_synthesized_tweet(
                topic=topic,
                mode="commentary",
                section_nums=section_nums,
                synthesis_mode="CHALLENGE",
                use_scenario=True,
                persona=persona_name,
            )

        return CommentaryResult(
            content=content,
            commentary_type="critical",
            sections_analyzed=len(content.citations) if content.citations else 0,
            ai_score=content.ai_score or 0.0,
            humanization_applied=content.humanization_applied,
        )

    async def generate_comparison(
        self,
        topic1: str,
        topic2: str,
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
    ) -> CommentaryResult:
        """Generate content comparing two topics/concepts.

        Creates a thread that explores the similarities,
        differences, and tensions between two concepts.

        Args:
            topic1: First topic to compare.
            topic2: Second topic to compare.
            section_nums: Optional specific sections.
            persona: Writing persona.

        Returns:
            CommentaryResult with comparison content.
        """
        persona_name = persona or self.default_persona
        combined_topic = f"Comparing {topic1} and {topic2}"

        content = await self.generator.generate_synthesized_thread(
            topic=combined_topic,
            num_tweets=5,
            mode="commentary",
            section_nums=section_nums,
            synthesis_mode="CONTRAST",
            use_scenario=False,
            persona=persona_name,
        )

        return CommentaryResult(
            content=content,
            commentary_type="comparison",
            sections_analyzed=len(content.citations) if content.citations else 0,
            ai_score=content.ai_score or 0.0,
            humanization_applied=content.humanization_applied,
        )

    async def generate_faq_response(
        self,
        question: str,
        section_nums: Optional[list[int]] = None,
        persona: Optional[str] = None,
    ) -> CommentaryResult:
        """Generate a response to a frequently asked question.

        Creates content that directly addresses a common question
        with insight and nuance.

        Args:
            question: The question to answer.
            section_nums: Optional specific sections.
            persona: Writing persona.

        Returns:
            CommentaryResult with FAQ response.
        """
        persona_name = persona or self.default_persona

        # FAQ responses work well as explanatory tweets
        content = await self.generator.generate_synthesized_tweet(
            topic=f"Question: {question}",
            mode="commentary",
            section_nums=section_nums,
            synthesis_mode="EXPLAIN",
            use_scenario=True,
            persona=persona_name,
        )

        return CommentaryResult(
            content=content,
            commentary_type="faq",
            sections_analyzed=len(content.citations) if content.citations else 0,
            ai_score=content.ai_score or 0.0,
            humanization_applied=content.humanization_applied,
        )

    def get_available_commentary_types(self) -> list[str]:
        """Get list of available commentary types."""
        return [
            "analysis",
            "myth_bust",
            "implications",
            "critical",
            "comparison",
            "faq",
        ]

    def get_available_personas(self) -> list[str]:
        """Get list of available writing personas."""
        return self.generator.get_available_personas()
