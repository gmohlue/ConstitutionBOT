"""Mode 1: Bot-proposed topics for content generation."""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.core.content.generator import ContentGenerator, GeneratedContent, TopicSuggestion


@dataclass
class BotProposedResult:
    """Result of bot-proposed content generation."""

    suggestion: TopicSuggestion
    content: GeneratedContent


class BotProposedMode:
    """Mode 1: Bot suggests topics and generates content.

    This mode is used for automated content generation where the bot
    proposes educational topics based on the Constitution and generates
    content for them.

    Workflow:
    1. Bot analyzes Constitution sections
    2. Suggests a relevant, educational topic
    3. Generates content (tweet/thread) for the topic
    4. Content goes to queue for admin review
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.generator = ContentGenerator(session)

    async def suggest_and_generate(
        self,
        content_type: str = "tweet",
        num_tweets: int = 5,
    ) -> BotProposedResult:
        """Suggest a topic and generate content for it.

        Args:
            content_type: "tweet" or "thread"
            num_tweets: Number of tweets if thread

        Returns:
            BotProposedResult with suggestion and generated content
        """
        # Get topic suggestion
        suggestion = await self.generator.suggest_topic()

        # Generate content based on suggestion
        if content_type == "thread":
            content = await self.generator.generate_thread(
                topic=suggestion.topic,
                num_tweets=num_tweets,
                mode="bot_proposed",
                section_nums=suggestion.section_nums,
            )
        else:
            content = await self.generator.generate_tweet(
                topic=suggestion.topic,
                mode="bot_proposed",
                section_nums=suggestion.section_nums,
            )

        return BotProposedResult(
            suggestion=suggestion,
            content=content,
        )

    async def suggest_only(self) -> TopicSuggestion:
        """Just suggest a topic without generating content.

        Useful when you want to preview topics before committing
        to content generation.
        """
        return await self.generator.suggest_topic()

    async def generate_from_suggestion(
        self,
        suggestion: TopicSuggestion,
        content_type: str = "tweet",
        num_tweets: int = 5,
    ) -> GeneratedContent:
        """Generate content from a previously obtained suggestion.

        Args:
            suggestion: A TopicSuggestion to generate content for
            content_type: "tweet" or "thread"
            num_tweets: Number of tweets if thread

        Returns:
            GeneratedContent for the topic
        """
        if content_type == "thread":
            return await self.generator.generate_thread(
                topic=suggestion.topic,
                num_tweets=num_tweets,
                mode="bot_proposed",
                section_nums=suggestion.section_nums,
            )
        else:
            return await self.generator.generate_tweet(
                topic=suggestion.topic,
                mode="bot_proposed",
                section_nums=suggestion.section_nums,
            )

    async def generate_section_spotlight(
        self,
        content_type: str = "tweet",
    ) -> BotProposedResult:
        """Generate content that spotlights a specific Constitution section.

        This randomly selects a section and creates educational content
        explaining its importance and relevance.
        """
        from contentmanager.core.document.retriever import DocumentRetriever

        retriever = DocumentRetriever(self.session)

        # Get a random section
        section = await retriever.get_random_section()
        if not section:
            raise ValueError("No constitution sections available")

        # Create suggestion based on the section
        suggestion = TopicSuggestion(
            topic=f"Understanding Section {section.section_num}: {section.section_title or 'A Key Right'}",
            section_nums=[section.section_num],
            angle="Section spotlight and explanation",
            reason="Highlighting an important constitutional provision",
        )

        # Generate explanation content
        content = await self.generator.explain_section(
            section_num=section.section_num,
            content_type=content_type,
        )
        content.mode = "bot_proposed"

        return BotProposedResult(
            suggestion=suggestion,
            content=content,
        )

    async def generate_bill_of_rights_focus(
        self,
        content_type: str = "tweet",
    ) -> BotProposedResult:
        """Generate content focused on the Bill of Rights (Chapter 2).

        The Bill of Rights is particularly important for civic education,
        so this method specifically targets those sections.
        """
        from contentmanager.core.document.retriever import DocumentRetriever
        import secrets

        retriever = DocumentRetriever(self.session)

        # Get Bill of Rights sections
        sections = await retriever.get_bill_of_rights_sections()
        if not sections:
            # Fallback to regular suggestion
            return await self.suggest_and_generate(content_type)

        # Pick a random section from Bill of Rights
        section = secrets.choice(sections)

        suggestion = TopicSuggestion(
            topic=f"Your Rights: Section {section.section_num} - {section.section_title or 'Bill of Rights'}",
            section_nums=[section.section_num],
            angle="Know your constitutional rights",
            reason="The Bill of Rights protects all South Africans",
        )

        content = await self.generator.explain_section(
            section_num=section.section_num,
            content_type=content_type,
        )
        content.mode = "bot_proposed"

        return BotProposedResult(
            suggestion=suggestion,
            content=content,
        )
