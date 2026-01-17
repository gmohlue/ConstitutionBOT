"""Content generator - main orchestrator for content creation."""

from dataclasses import dataclass
from typing import Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.core.claude_client import ClaudeClient, get_claude_client
from constitutionbot.core.constitution.retriever import ConstitutionRetriever
from constitutionbot.core.content.formats import ContentFormatter, Script, Thread, Tweet
from constitutionbot.core.content.templates import PromptTemplates
from constitutionbot.core.content.validators import ContentValidator, ValidationResult
from constitutionbot.core.llm import LLMProvider, get_llm_provider
from constitutionbot.database.models import ConstitutionSection


@dataclass
class GeneratedContent:
    """Container for generated content with metadata."""

    content_type: str  # tweet, thread, script
    raw_content: str
    formatted_content: str
    topic: Optional[str] = None
    citations: Optional[list[dict]] = None
    validation: Optional[ValidationResult] = None
    mode: str = "bot_proposed"  # bot_proposed, user_provided, historical


@dataclass
class TopicSuggestion:
    """A suggested topic for content generation."""

    topic: str
    section_nums: list[int]
    angle: str
    reason: str


class ContentGenerator:
    """Generate educational content about the SA Constitution."""

    def __init__(
        self,
        session: AsyncSession,
        llm_provider: Optional[Union[LLMProvider, ClaudeClient]] = None,
        claude_client: Optional[ClaudeClient] = None,  # Deprecated, for backward compat
    ):
        self.session = session
        self.retriever = ConstitutionRetriever(session)
        # Support both new llm_provider and deprecated claude_client parameter
        self._llm_provider = llm_provider or claude_client
        self._llm_initialized = False
        self.formatter = ContentFormatter()
        self.validator = ContentValidator()

    async def _get_llm(self) -> Union[LLMProvider, ClaudeClient]:
        """Get the LLM provider, initializing if needed."""
        if self._llm_provider is not None:
            return self._llm_provider
        if not self._llm_initialized:
            self._llm_provider = await get_llm_provider(self.session)
            self._llm_initialized = True
        return self._llm_provider

    @property
    def claude(self) -> Union[LLMProvider, ClaudeClient]:
        """Backward compatibility property. Use _get_llm() for async contexts."""
        if self._llm_provider is None:
            # Fallback for synchronous access (backward compatibility)
            self._llm_provider = get_claude_client()
        return self._llm_provider

    async def suggest_topic(self) -> TopicSuggestion:
        """Generate a topic suggestion (Mode 1: Bot Proposed)."""
        # Get some random sections for inspiration
        sections = []
        for _ in range(3):
            section = await self.retriever.get_random_section()
            if section:
                sections.append(section)

        context = ""
        if sections:
            context = await self.retriever.format_multiple_sections(sections)

        prompt = PromptTemplates.TOPIC_SUGGESTION_PROMPT
        if context:
            prompt = f"Here are some constitutional sections for inspiration:\n\n{context}\n\n{prompt}"

        llm = await self._get_llm()
        response = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            temperature=0.8,
        )

        # Parse the response
        return self._parse_topic_suggestion(response)

    def _parse_topic_suggestion(self, response: str) -> TopicSuggestion:
        """Parse topic suggestion from Claude's response."""
        import re

        topic = ""
        section_nums = []
        angle = ""
        reason = ""

        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("TOPIC:"):
                topic = line.replace("TOPIC:", "").strip()
            elif line.startswith("SECTION:"):
                section_str = line.replace("SECTION:", "").strip()
                section_nums = [int(n) for n in re.findall(r"\d+", section_str)]
            elif line.startswith("ANGLE:"):
                angle = line.replace("ANGLE:", "").strip()
            elif line.startswith("WHY:"):
                reason = line.replace("WHY:", "").strip()

        return TopicSuggestion(
            topic=topic or "Constitutional rights and civic education",
            section_nums=section_nums or [9],  # Default to equality section
            angle=angle or "Educational overview",
            reason=reason or "Relevant to South African citizens",
        )

    async def generate_tweet(
        self,
        topic: str,
        mode: str = "user_provided",
        section_nums: Optional[list[int]] = None,
    ) -> GeneratedContent:
        """Generate a single educational tweet."""
        # Get relevant sections
        if section_nums:
            sections = []
            for num in section_nums:
                section = await self.retriever.get_section(num)
                if section:
                    sections.append(section)
        else:
            sections = await self.retriever.get_sections_for_topic(topic, limit=3)

        # Format context
        context = await self.retriever.format_multiple_sections(sections) if sections else ""

        # Generate content
        prompt = PromptTemplates.get_tweet_prompt(topic=topic, context=context)
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            temperature=0.7,
        )

        # Parse and format
        tweet = self.formatter.parse_tweet(raw_content)
        formatted = self.formatter.format_tweet_for_posting(tweet)
        formatted = self.formatter.add_hashtags(formatted)

        # Validate
        validation = self.validator.validate_tweet(formatted)

        # Build citations
        citations = self._build_citations(sections)

        return GeneratedContent(
            content_type="tweet",
            raw_content=raw_content,
            formatted_content=formatted,
            topic=topic,
            citations=citations,
            validation=validation,
            mode=mode,
        )

    async def generate_thread(
        self,
        topic: str,
        num_tweets: int = 5,
        mode: str = "user_provided",
        section_nums: Optional[list[int]] = None,
    ) -> GeneratedContent:
        """Generate a Twitter thread."""
        # Get relevant sections
        if section_nums:
            sections = []
            for num in section_nums:
                section = await self.retriever.get_section(num)
                if section:
                    sections.append(section)
        else:
            sections = await self.retriever.get_sections_for_topic(topic, limit=5)

        # Format context
        context = await self.retriever.format_multiple_sections(sections) if sections else ""

        # Generate content
        prompt = PromptTemplates.get_thread_prompt(
            topic=topic,
            context=context,
            num_tweets=num_tweets,
        )
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=2000,
        )

        # Parse and format
        thread = self.formatter.parse_thread(raw_content, topic=topic)
        formatted_tweets = self.formatter.format_thread_for_posting(thread)
        formatted = thread.format_for_storage()

        # Validate
        validation = self.validator.validate_thread(formatted_tweets)

        # Build citations
        citations = self._build_citations(sections)

        return GeneratedContent(
            content_type="thread",
            raw_content=raw_content,
            formatted_content=formatted,
            topic=topic,
            citations=citations,
            validation=validation,
            mode=mode,
        )

    async def generate_script(
        self,
        topic: str,
        mode: str = "user_provided",
        section_nums: Optional[list[int]] = None,
        duration: str = "2-3 minutes",
    ) -> GeneratedContent:
        """Generate a dialog script for educational content."""
        # Get relevant sections
        if section_nums:
            sections = []
            for num in section_nums:
                section = await self.retriever.get_section(num)
                if section:
                    sections.append(section)
        else:
            sections = await self.retriever.get_sections_for_topic(topic, limit=5)

        # Format context
        context = await self.retriever.format_multiple_sections(sections) if sections else ""

        # Generate content
        prompt = PromptTemplates.get_script_prompt(
            topic=topic,
            context=context,
            duration=duration,
        )
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=3000,
        )

        # Parse and format
        script = self.formatter.parse_script(raw_content, title=topic)
        formatted = raw_content  # Store the full script as-is

        # Build citations
        citations = self._build_citations(sections)

        return GeneratedContent(
            content_type="script",
            raw_content=raw_content,
            formatted_content=formatted,
            topic=topic,
            citations=citations,
            validation=None,  # Scripts don't have character limits
            mode=mode,
        )

    async def generate_reply(
        self,
        mention_text: str,
        mention_author: str,
    ) -> GeneratedContent:
        """Generate a reply to a mention."""
        # Find relevant sections based on mention content
        sections = await self.retriever.get_sections_for_topic(mention_text, limit=3)

        # Format context
        context = await self.retriever.format_multiple_sections(sections) if sections else ""

        # Generate content
        prompt = PromptTemplates.get_reply_prompt(
            username=mention_author,
            mention_text=mention_text,
            context=context,
        )
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            temperature=0.6,
        )

        # Parse and format
        tweet = self.formatter.parse_tweet(raw_content)
        formatted = self.formatter.format_tweet_for_posting(tweet)

        # Validate as reply
        validation = self.validator.validate_reply(formatted, mention_text)

        # Build citations
        citations = self._build_citations(sections)

        return GeneratedContent(
            content_type="tweet",
            raw_content=raw_content,
            formatted_content=formatted,
            topic=f"Reply to @{mention_author}",
            citations=citations,
            validation=validation,
            mode="user_provided",
        )

    async def generate_historical(
        self,
        event: str,
        content_type: str = "tweet",
    ) -> GeneratedContent:
        """Generate content about a historical event (Mode 3)."""
        # Search for relevant sections
        sections = await self.retriever.get_sections_for_topic(event, limit=5)

        # Format context
        context = await self.retriever.format_multiple_sections(sections) if sections else ""

        # Determine format requirements
        if content_type == "thread":
            format_requirements = "Create a 5-tweet thread explaining the connection"
        else:
            format_requirements = "Maximum 280 characters with hashtags"

        # Generate content
        prompt = PromptTemplates.get_historical_prompt(
            event=event,
            context=context,
            format_type=content_type,
            format_requirements=format_requirements,
        )
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            temperature=0.7,
        )

        # Parse based on type
        if content_type == "thread":
            thread = self.formatter.parse_thread(raw_content, topic=event)
            formatted = thread.format_for_storage()
            formatted_tweets = self.formatter.format_thread_for_posting(thread)
            validation = self.validator.validate_thread(formatted_tweets)
        else:
            tweet = self.formatter.parse_tweet(raw_content)
            formatted = self.formatter.format_tweet_for_posting(tweet)
            formatted = self.formatter.add_hashtags(formatted)
            validation = self.validator.validate_tweet(formatted)

        # Build citations
        citations = self._build_citations(sections)

        return GeneratedContent(
            content_type=content_type,
            raw_content=raw_content,
            formatted_content=formatted,
            topic=event,
            citations=citations,
            validation=validation,
            mode="historical",
        )

    async def explain_section(
        self,
        section_num: int,
        content_type: str = "tweet",
    ) -> GeneratedContent:
        """Generate an explanation of a specific section."""
        section = await self.retriever.get_section(section_num)
        if not section:
            raise ValueError(f"Section {section_num} not found")

        section_text = await self.retriever.format_section_for_prompt(section)

        # Determine format
        if content_type == "thread":
            max_length = "5-tweet thread"
        else:
            max_length = "280 characters"

        # Generate content
        prompt = PromptTemplates.get_explainer_prompt(
            section_text=section_text,
            format_type=content_type,
            max_length=max_length,
        )
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            temperature=0.7,
        )

        # Parse based on type
        topic = f"Section {section_num}: {section.section_title or 'Explanation'}"

        if content_type == "thread":
            thread = self.formatter.parse_thread(raw_content, topic=topic)
            formatted = thread.format_for_storage()
            formatted_tweets = self.formatter.format_thread_for_posting(thread)
            validation = self.validator.validate_thread(formatted_tweets)
        else:
            tweet = self.formatter.parse_tweet(raw_content)
            formatted = self.formatter.format_tweet_for_posting(tweet)
            formatted = self.formatter.add_hashtags(formatted)
            validation = self.validator.validate_tweet(formatted)

        # Build citations
        citations = self._build_citations([section])

        return GeneratedContent(
            content_type=content_type,
            raw_content=raw_content,
            formatted_content=formatted,
            topic=topic,
            citations=citations,
            validation=validation,
            mode="user_provided",
        )

    def _build_citations(self, sections: list[ConstitutionSection]) -> list[dict]:
        """Build citation references from sections."""
        citations = []
        for section in sections:
            citations.append({
                "section_num": section.section_num,
                "section_title": section.section_title,
                "chapter_num": section.chapter_num,
                "chapter_title": section.chapter_title,
            })
        return citations
