"""Content generator - main orchestrator for content creation."""

from dataclasses import dataclass, field
from typing import Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.core.claude_client import ClaudeClient, get_claude_client
from contentmanager.core.document import DocumentContext, DocumentRetriever
from contentmanager.core.content.formats import ContentFormatter, Script, Thread, Tweet
from contentmanager.core.content.templates import DEFAULT_DOCUMENT_CONTEXT, PromptTemplates
from contentmanager.core.content.validators import ContentValidator, ValidationResult
from contentmanager.core.llm import LLMProvider, get_llm_provider
from contentmanager.database.models import DocumentSection

# Synthesis system imports
from contentmanager.core.content.ai_pattern_filter import AIPatternFilter, AIPatternReport
from contentmanager.core.content.insight_analyzer import InsightAnalyzer, SectionInsight
from contentmanager.core.content.synthesis import SynthesisEngine, SynthesisMode, SynthesisContext
from contentmanager.core.content.scenarios import ScenarioGenerator, Scenario
from contentmanager.core.content.persona_writer import PersonaWriter, WritingPersona, PERSONAS
from contentmanager.core.content.prompt_variants import PromptVariants
from contentmanager.core.content.concept_mapper import ConceptMapper


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

    # Synthesis metadata
    synthesis_mode: Optional[str] = None
    ai_score: Optional[float] = None
    persona_used: Optional[str] = None
    scenario_used: Optional[str] = None
    humanization_applied: bool = False


@dataclass
class TopicSuggestion:
    """A suggested topic for content generation."""

    topic: str
    section_nums: list[int]
    angle: str
    reason: str


class ContentGenerator:
    """Generate educational content from any document."""

    def __init__(
        self,
        session: AsyncSession,
        llm_provider: Optional[Union[LLMProvider, ClaudeClient]] = None,
        claude_client: Optional[ClaudeClient] = None,  # Deprecated, for backward compat
        document_id: Optional[int] = None,
        # Synthesis settings
        default_synthesis_mode: str = "CHALLENGE",
        ai_pattern_threshold: float = 0.5,
        humanization_retries: int = 2,
        default_persona: str = "conversational",
        use_scenarios: bool = True,
    ):
        self.session = session
        self.retriever = DocumentRetriever(session, document_id)
        # Support both new llm_provider and deprecated claude_client parameter
        self._llm_provider = llm_provider or claude_client
        self._llm_initialized = False
        self.formatter = ContentFormatter()
        self.validator = ContentValidator()
        self._doc_context: Optional[DocumentContext] = None

        # Synthesis system components
        self.insight_analyzer = InsightAnalyzer()
        self.synthesis_engine = SynthesisEngine()
        self.persona_writer = PersonaWriter(default_persona)
        self.ai_filter = AIPatternFilter()
        self.scenario_generator = ScenarioGenerator()
        self.prompt_variants = PromptVariants()
        self.concept_mapper = ConceptMapper()

        # Synthesis settings
        self.default_synthesis_mode = default_synthesis_mode
        self.ai_pattern_threshold = ai_pattern_threshold
        self.humanization_retries = humanization_retries
        self.default_persona = default_persona
        self.use_scenarios = use_scenarios

    async def _get_llm(self) -> Union[LLMProvider, ClaudeClient]:
        """Get the LLM provider, initializing if needed."""
        if self._llm_provider is not None:
            return self._llm_provider
        if not self._llm_initialized:
            self._llm_provider = await get_llm_provider(self.session)
            self._llm_initialized = True
        return self._llm_provider

    async def _get_doc_context(self) -> DocumentContext:
        """Get the document context, fetching from DB if needed."""
        if self._doc_context:
            return self._doc_context

        doc = await self.retriever.get_document()
        if doc:
            section_label = await self.retriever.get_section_label()
            self._doc_context = DocumentContext(
                document_name=doc.name,
                document_short_name=doc.short_name,
                section_label=section_label,
                description=doc.description,
                default_hashtags=doc.default_hashtags or [],
            )
        else:
            self._doc_context = DEFAULT_DOCUMENT_CONTEXT

        return self._doc_context

    @property
    def claude(self) -> Union[LLMProvider, ClaudeClient]:
        """Backward compatibility property. Use _get_llm() for async contexts."""
        if self._llm_provider is None:
            # Fallback for synchronous access (backward compatibility)
            self._llm_provider = get_claude_client()
        return self._llm_provider

    async def suggest_topic(self) -> TopicSuggestion:
        """Generate a topic suggestion (Mode 1: Bot Proposed)."""
        # Get document context
        doc_context = await self._get_doc_context()

        # Get some random sections for inspiration
        sections = []
        for _ in range(3):
            section = await self.retriever.get_random_section()
            if section:
                sections.append(section)

        context = ""
        if sections:
            context = await self.retriever.format_multiple_sections(sections)

        prompt = PromptTemplates.get_topic_suggestion_prompt(doc_context=doc_context)
        if context:
            prompt = f"Here are some {doc_context.section_label.lower()}s for inspiration:\n\n{context}\n\n{prompt}"

        llm = await self._get_llm()
        response = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
            temperature=0.8,
        )

        # Parse the response
        return self._parse_topic_suggestion(response, doc_context)

    def _parse_topic_suggestion(
        self,
        response: str,
        doc_context: Optional[DocumentContext] = None,
    ) -> TopicSuggestion:
        """Parse topic suggestion from Claude's response."""
        import re

        ctx = doc_context or DEFAULT_DOCUMENT_CONTEXT
        section_label = ctx.section_label.upper()

        topic = ""
        section_nums = []
        angle = ""
        reason = ""

        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("TOPIC:"):
                topic = line.replace("TOPIC:", "").strip()
            elif line.startswith(f"{section_label}:"):
                section_str = line.replace(f"{section_label}:", "").strip()
                section_nums = [int(n) for n in re.findall(r"\d+", section_str)]
            elif line.startswith("SECTION:"):  # Backward compat
                section_str = line.replace("SECTION:", "").strip()
                section_nums = [int(n) for n in re.findall(r"\d+", section_str)]
            elif line.startswith("ANGLE:"):
                angle = line.replace("ANGLE:", "").strip()
            elif line.startswith("WHY:"):
                reason = line.replace("WHY:", "").strip()

        return TopicSuggestion(
            topic=topic or f"{ctx.document_short_name} education",
            section_nums=section_nums or [1],  # Default to first section
            angle=angle or "Educational overview",
            reason=reason or "Relevant to the audience",
        )

    async def generate_tweet(
        self,
        topic: str,
        mode: str = "user_provided",
        section_nums: Optional[list[int]] = None,
    ) -> GeneratedContent:
        """Generate a single educational tweet."""
        # Get document context
        doc_context = await self._get_doc_context()

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

        # If no direct sections found, try concept-based synthesis
        if not sections and not context:
            concept_context = self.concept_mapper.build_context_for_synthesis(topic)
            if concept_context:
                # Use concept-based generation
                return await self._generate_concept_tweet(
                    topic=topic,
                    concept_context=concept_context,
                    doc_context=doc_context,
                    mode=mode,
                )

        # Generate content
        prompt = PromptTemplates.get_tweet_prompt(
            topic=topic,
            context=context,
            doc_context=doc_context,
        )
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
            temperature=0.7,
        )

        # Parse and format
        tweet = self.formatter.parse_tweet(raw_content)
        formatted = self.formatter.format_tweet_for_posting(tweet)
        formatted = self.formatter.add_hashtags(formatted, doc_context.default_hashtags)

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
        # Get document context
        doc_context = await self._get_doc_context()

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

        # If no direct sections found, try concept-based synthesis
        if not sections and not context:
            concept_context = self.concept_mapper.build_context_for_synthesis(topic)
            if concept_context:
                # Use concept-based generation
                return await self._generate_concept_thread(
                    topic=topic,
                    concept_context=concept_context,
                    num_tweets=num_tweets,
                    doc_context=doc_context,
                    mode=mode,
                )

        # Generate content
        prompt = PromptTemplates.get_thread_prompt(
            topic=topic,
            context=context,
            num_tweets=num_tweets,
            doc_context=doc_context,
        )
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
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
        # Get document context
        doc_context = await self._get_doc_context()

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

        # If no direct sections found, try concept-based synthesis
        if not sections and not context:
            concept_context = self.concept_mapper.build_context_for_synthesis(topic)
            if concept_context:
                # Use concept-based generation
                return await self._generate_concept_script(
                    topic=topic,
                    concept_context=concept_context,
                    duration=duration,
                    doc_context=doc_context,
                    mode=mode,
                )

        # Generate content
        prompt = PromptTemplates.get_script_prompt(
            topic=topic,
            context=context,
            duration=duration,
            doc_context=doc_context,
        )
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
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
        # Get document context
        doc_context = await self._get_doc_context()

        # Find relevant sections based on mention content
        sections = await self.retriever.get_sections_for_topic(mention_text, limit=3)

        # Format context
        context = await self.retriever.format_multiple_sections(sections) if sections else ""

        # Generate content
        prompt = PromptTemplates.get_reply_prompt(
            username=mention_author,
            mention_text=mention_text,
            context=context,
            doc_context=doc_context,
        )
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
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

    async def generate_external_tweet_reply(
        self,
        tweet_text: str,
        author: str,
        stance: str,
        tone: str = "respectful but firm",
        focus: str | None = None,
    ) -> GeneratedContent:
        """Generate a reply to an external tweet based on constitutional principles.

        Args:
            tweet_text: The text of the tweet to reply to
            author: The username of the tweet author (without @)
            stance: 'agree', 'disagree', or 'neutral'
            tone: The tone for the reply
            focus: Optional specific focus area or section

        Returns:
            GeneratedContent with the generated reply
        """
        # Get document context
        doc_context = await self._get_doc_context()

        # Find relevant sections based on tweet content
        sections = await self.retriever.get_sections_for_topic(tweet_text, limit=3)

        # If focus is specified, also search for that
        if focus:
            focus_sections = await self.retriever.get_sections_for_topic(focus, limit=2)
            # Merge sections, avoiding duplicates
            existing_nums = {s.section_num for s in sections}
            for s in focus_sections:
                if s.section_num not in existing_nums:
                    sections.append(s)

        # If no sections found, try concept mapping
        context = ""
        if sections:
            context = await self.retriever.format_multiple_sections(sections)
        else:
            # Try concept-based context
            concept_context = self.concept_mapper.build_context_for_synthesis(tweet_text)
            if concept_context:
                context = concept_context

        # Build additional guidance if focus is provided
        additional_guidance = ""
        if focus:
            additional_guidance = f"Focus your response on: {focus}"

        # Generate content
        prompt = PromptTemplates.get_external_tweet_reply_prompt(
            tweet_text=tweet_text,
            author=author,
            stance=stance,
            context=context,
            tone=tone,
            additional_guidance=additional_guidance,
            doc_context=doc_context,
        )

        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
            temperature=0.7,
        )

        # Parse and format
        tweet = self.formatter.parse_tweet(raw_content)
        formatted = self.formatter.format_tweet_for_posting(tweet)

        # Validate as reply
        validation = self.validator.validate_reply(formatted, tweet_text)

        # Build citations
        citations = self._build_citations(sections)

        return GeneratedContent(
            content_type="reply",
            raw_content=raw_content,
            formatted_content=formatted,
            topic=f"Reply to @{author} ({stance})",
            citations=citations,
            validation=validation,
            mode="external_reply",
        )

    async def generate_historical(
        self,
        event: str,
        content_type: str = "tweet",
    ) -> GeneratedContent:
        """Generate content about a historical event (Mode 3)."""
        # Get document context
        doc_context = await self._get_doc_context()

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
            doc_context=doc_context,
        )
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
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
            formatted = self.formatter.add_hashtags(formatted, doc_context.default_hashtags)
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
        # Get document context
        doc_context = await self._get_doc_context()
        section_label = doc_context.section_label

        section = await self.retriever.get_section(section_num)
        if not section:
            raise ValueError(f"{section_label} {section_num} not found")

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
            doc_context=doc_context,
        )
        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
            temperature=0.7,
        )

        # Parse based on type
        topic = f"{section_label} {section_num}: {section.section_title or 'Explanation'}"

        if content_type == "thread":
            thread = self.formatter.parse_thread(raw_content, topic=topic)
            formatted = thread.format_for_storage()
            formatted_tweets = self.formatter.format_thread_for_posting(thread)
            validation = self.validator.validate_thread(formatted_tweets)
        else:
            tweet = self.formatter.parse_tweet(raw_content)
            formatted = self.formatter.format_tweet_for_posting(tweet)
            formatted = self.formatter.add_hashtags(formatted, doc_context.default_hashtags)
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

    def _build_citations(self, sections: list[DocumentSection]) -> list[dict]:
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

    # ========================================================================
    # CONCEPT-BASED GENERATION - For topics without direct document matches
    # ========================================================================

    async def _generate_concept_tweet(
        self,
        topic: str,
        concept_context: str,
        doc_context: DocumentContext,
        mode: str = "user_provided",
    ) -> GeneratedContent:
        """Generate a tweet using concept-based synthesis.

        Used when no direct document sections match the topic, but we can
        map it to constitutional principles conceptually.
        """
        # Get persona
        persona_obj = self.persona_writer.get_persona(self.default_persona)
        persona_description = persona_obj.to_prompt_description() if persona_obj else "conversational"

        # Generate with concept prompt
        prompt = PromptTemplates.get_concept_tweet_prompt(
            topic=topic,
            concept_context=concept_context,
            persona_description=persona_description,
            doc_context=doc_context,
        )

        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
            temperature=0.8,  # Higher for creative synthesis
        )

        # Apply humanization if needed
        formatted = raw_content.strip()
        humanization_applied = False
        ai_score = 0.0

        for attempt in range(self.humanization_retries + 1):
            is_human_like, report = self.ai_filter.validate_human_likeness(
                formatted, self.ai_pattern_threshold
            )
            ai_score = report.ai_score

            if is_human_like:
                break

            result = self.persona_writer.humanize_content(formatted, persona_obj)
            formatted = result.transformed
            humanization_applied = True

            if attempt < self.humanization_retries:
                formatted = self.ai_filter.humanize(formatted)

        # Parse and format
        tweet = self.formatter.parse_tweet(formatted)
        final_content = self.formatter.format_tweet_for_posting(tweet)
        final_content = self.formatter.add_hashtags(final_content, doc_context.default_hashtags)

        # Validate
        validation = self.validator.validate_with_ai_check(
            final_content, "tweet", self.ai_pattern_threshold
        )

        # Build citations from concept mapping
        mapping = self.concept_mapper.map_topic(topic)
        citations = []
        if mapping:
            for section_num in mapping.section_references:
                citations.append({
                    "section_num": section_num,
                    "section_title": f"Related to {topic}",
                    "chapter_num": None,
                    "chapter_title": None,
                })

        return GeneratedContent(
            content_type="tweet",
            raw_content=raw_content,
            formatted_content=final_content,
            topic=topic,
            citations=citations,
            validation=validation,
            mode=mode,
            synthesis_mode="CONCEPT",
            ai_score=ai_score,
            persona_used=self.default_persona,
            humanization_applied=humanization_applied,
        )

    async def _generate_concept_thread(
        self,
        topic: str,
        concept_context: str,
        num_tweets: int,
        doc_context: DocumentContext,
        mode: str = "user_provided",
    ) -> GeneratedContent:
        """Generate a thread using concept-based synthesis.

        Used when no direct document sections match the topic, but we can
        map it to constitutional principles conceptually.
        """
        # Get persona and thread structure
        persona_obj = self.persona_writer.get_persona(self.default_persona)
        persona_description = persona_obj.to_prompt_description() if persona_obj else "conversational"
        thread_config = self.prompt_variants.get_thread_structure()
        thread_structure = thread_config.get("tone", "progressive revelation")

        # Generate with concept prompt
        prompt = PromptTemplates.get_concept_thread_prompt(
            topic=topic,
            concept_context=concept_context,
            num_tweets=num_tweets,
            thread_structure=thread_structure,
            persona_description=persona_description,
            doc_context=doc_context,
        )

        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
            temperature=0.8,
            max_tokens=2000,
        )

        # Parse thread
        thread = self.formatter.parse_thread(raw_content, topic=topic)

        # Humanize each tweet
        humanization_applied = False
        total_ai_score = 0.0

        for tweet in thread.tweets:
            formatted = tweet.content

            for attempt in range(self.humanization_retries + 1):
                is_human_like, report = self.ai_filter.validate_human_likeness(
                    formatted, self.ai_pattern_threshold
                )
                total_ai_score += report.ai_score

                if is_human_like:
                    break

                result = self.persona_writer.humanize_content(formatted, persona_obj)
                formatted = result.transformed
                humanization_applied = True

                if attempt < self.humanization_retries:
                    formatted = self.ai_filter.humanize(formatted)

            tweet.content = formatted

        avg_ai_score = total_ai_score / len(thread.tweets) if thread.tweets else 0.0

        # Format for posting
        formatted_tweets = self.formatter.format_thread_for_posting(thread)
        formatted = thread.format_for_storage()

        # Validate
        validation = self.validator.validate_thread(formatted_tweets)

        # Build citations from concept mapping
        mapping = self.concept_mapper.map_topic(topic)
        citations = []
        if mapping:
            for section_num in mapping.section_references:
                citations.append({
                    "section_num": section_num,
                    "section_title": f"Related to {topic}",
                    "chapter_num": None,
                    "chapter_title": None,
                })

        return GeneratedContent(
            content_type="thread",
            raw_content=raw_content,
            formatted_content=formatted,
            topic=topic,
            citations=citations,
            validation=validation,
            mode=mode,
            synthesis_mode="CONCEPT",
            ai_score=avg_ai_score,
            persona_used=self.default_persona,
            humanization_applied=humanization_applied,
        )

    async def _generate_concept_script(
        self,
        topic: str,
        concept_context: str,
        duration: str,
        doc_context: DocumentContext,
        mode: str = "user_provided",
    ) -> GeneratedContent:
        """Generate a dialog script using concept-based synthesis.

        Used when no direct document sections match the topic, but we can
        map it to constitutional principles conceptually.
        """
        # Get persona
        persona_obj = self.persona_writer.get_persona(self.default_persona)
        persona_description = persona_obj.to_prompt_description() if persona_obj else "conversational"

        # Generate with concept prompt
        prompt = PromptTemplates.get_concept_script_prompt(
            topic=topic,
            concept_context=concept_context,
            duration=duration,
            persona_description=persona_description,
            doc_context=doc_context,
        )

        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
            temperature=0.8,
            max_tokens=3000,
        )

        # Parse and format
        script = self.formatter.parse_script(raw_content, title=topic)
        formatted = raw_content  # Store the full script as-is

        # Build citations from concept mapping
        mapping = self.concept_mapper.map_topic(topic)
        citations = []
        if mapping:
            for section_num in mapping.section_references:
                citations.append({
                    "section_num": section_num,
                    "section_title": f"Related to {topic}",
                    "chapter_num": None,
                    "chapter_title": None,
                })

        return GeneratedContent(
            content_type="script",
            raw_content=raw_content,
            formatted_content=formatted,
            topic=topic,
            citations=citations,
            validation=None,  # Scripts don't have character limits
            mode=mode,
            synthesis_mode="CONCEPT",
            persona_used=self.default_persona,
        )

    # ========================================================================
    # SYNTHESIS METHODS - Intelligent content synthesis pipeline
    # ========================================================================

    async def generate_synthesized_tweet(
        self,
        topic: str,
        mode: str = "user_provided",
        section_nums: Optional[list[int]] = None,
        synthesis_mode: Optional[str] = None,
        use_scenario: bool = True,
        persona: Optional[str] = None,
    ) -> GeneratedContent:
        """Generate a tweet using the full synthesis pipeline.

        This replaces simple extraction with intelligent synthesis:
        1. Analyze sections for insights
        2. Generate scenario context
        3. Synthesize original content
        4. Apply human voice
        5. Filter AI patterns with retry

        Args:
            topic: The topic to generate content about.
            mode: Generation mode (user_provided, bot_proposed, historical).
            section_nums: Optional specific sections to use.
            synthesis_mode: Synthesis mode (EXPLAIN, CONTRAST, CHALLENGE, etc.).
            use_scenario: Whether to include scenario context.
            persona: Persona name to use (conversational, thoughtful, etc.).

        Returns:
            GeneratedContent with synthesis metadata.
        """
        doc_context = await self._get_doc_context()
        synthesis_mode = synthesis_mode or self.default_synthesis_mode
        persona_name = persona or self.default_persona

        # Get relevant sections
        if section_nums:
            sections = []
            for num in section_nums:
                section = await self.retriever.get_section(num)
                if section:
                    sections.append(section)
        else:
            sections = await self.retriever.get_sections_for_topic(topic, limit=3)

        if not sections:
            # Try concept-based synthesis if no sections found
            concept_context = self.concept_mapper.build_context_for_synthesis(topic)
            if concept_context:
                return await self._generate_concept_tweet(
                    topic=topic,
                    concept_context=concept_context,
                    doc_context=doc_context,
                    mode=mode,
                )
            # Fall back to standard generation only if no concept mapping exists
            return await self.generate_tweet(topic, mode, section_nums)

        # Step 1: Analyze sections for insights
        insights = []
        for section in sections:
            insight = await self.insight_analyzer.analyze_section(section, use_llm=False)
            insights.append(insight)

        # Step 2: Generate scenario context
        scenario = None
        scenario_text = ""
        if use_scenario and self.use_scenarios:
            keywords = []
            for insight in insights:
                keywords.extend(insight.keywords)
            scenario = self.scenario_generator.match_scenario_to_topic(topic, keywords)
            scenario_text = scenario.to_prompt_context()

        # Step 3: Build insight context for prompt
        insight_context = "\n\n".join(i.to_prompt_context() for i in insights)

        # Step 4: Get persona
        persona_obj = self.persona_writer.get_persona(persona_name)
        persona_description = persona_obj.to_prompt_description() if persona_obj else "conversational"

        # Step 5: Generate with synthesis prompt
        prompt = PromptTemplates.get_tweet_synthesis_prompt(
            topic=topic,
            insight_context=insight_context,
            scenario=scenario_text,
            persona_description=persona_description,
            doc_context=doc_context,
        )

        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
            temperature=0.8,  # Slightly higher for creativity
        )

        # Step 6: Humanize and filter with retry loop
        formatted = raw_content.strip()
        humanization_applied = False
        ai_score = 0.0

        for attempt in range(self.humanization_retries + 1):
            # Check AI patterns
            is_human_like, report = self.ai_filter.validate_human_likeness(
                formatted, self.ai_pattern_threshold
            )
            ai_score = report.ai_score

            if is_human_like:
                break

            # Apply humanization
            result = self.persona_writer.humanize_content(formatted, persona_obj)
            formatted = result.transformed
            humanization_applied = True

            # If still not human-like after humanization, try auto-humanize
            if attempt < self.humanization_retries:
                formatted = self.ai_filter.humanize(formatted)

        # Parse and format final content
        tweet = self.formatter.parse_tweet(formatted)
        final_content = self.formatter.format_tweet_for_posting(tweet)
        final_content = self.formatter.add_hashtags(final_content, doc_context.default_hashtags)

        # Validate
        validation = self.validator.validate_with_ai_check(
            final_content, "tweet", self.ai_pattern_threshold
        )

        # Build citations
        citations = self._build_citations(sections)

        return GeneratedContent(
            content_type="tweet",
            raw_content=raw_content,
            formatted_content=final_content,
            topic=topic,
            citations=citations,
            validation=validation,
            mode=mode,
            synthesis_mode=synthesis_mode,
            ai_score=ai_score,
            persona_used=persona_name,
            scenario_used=scenario.category.value if scenario else None,
            humanization_applied=humanization_applied,
        )

    async def generate_synthesized_thread(
        self,
        topic: str,
        num_tweets: int = 5,
        mode: str = "user_provided",
        section_nums: Optional[list[int]] = None,
        synthesis_mode: Optional[str] = None,
        use_scenario: bool = True,
        persona: Optional[str] = None,
    ) -> GeneratedContent:
        """Generate a thread using the full synthesis pipeline.

        Args:
            topic: The topic to generate content about.
            num_tweets: Number of tweets in the thread.
            mode: Generation mode.
            section_nums: Optional specific sections to use.
            synthesis_mode: Synthesis mode to use.
            use_scenario: Whether to include scenario context.
            persona: Persona name to use.

        Returns:
            GeneratedContent with synthesis metadata.
        """
        doc_context = await self._get_doc_context()
        synthesis_mode = synthesis_mode or self.default_synthesis_mode
        persona_name = persona or self.default_persona

        # Get relevant sections
        if section_nums:
            sections = []
            for num in section_nums:
                section = await self.retriever.get_section(num)
                if section:
                    sections.append(section)
        else:
            sections = await self.retriever.get_sections_for_topic(topic, limit=5)

        if not sections:
            # Try concept-based synthesis if no sections found
            concept_context = self.concept_mapper.build_context_for_synthesis(topic)
            if concept_context:
                return await self._generate_concept_thread(
                    topic=topic,
                    concept_context=concept_context,
                    num_tweets=num_tweets,
                    doc_context=doc_context,
                    mode=mode,
                )
            return await self.generate_thread(topic, num_tweets, mode, section_nums)

        # Analyze sections for insights
        insights = []
        for section in sections:
            insight = await self.insight_analyzer.analyze_section(section, use_llm=False)
            insights.append(insight)

        # Generate scenario context
        scenario = None
        scenario_text = ""
        if use_scenario and self.use_scenarios:
            keywords = []
            for insight in insights:
                keywords.extend(insight.keywords)
            scenario = self.scenario_generator.match_scenario_to_topic(topic, keywords)
            scenario_text = scenario.to_prompt_context()

        # Build insight context
        insight_context = "\n\n".join(i.to_prompt_context() for i in insights)

        # Get thread structure variant
        thread_config = self.prompt_variants.get_thread_structure()
        thread_structure = thread_config.get("tone", "progressive revelation")

        # Get persona
        persona_obj = self.persona_writer.get_persona(persona_name)
        persona_description = persona_obj.to_prompt_description() if persona_obj else "conversational"

        # Generate with synthesis prompt
        prompt = PromptTemplates.get_thread_synthesis_prompt(
            topic=topic,
            insight_context=insight_context,
            num_tweets=num_tweets,
            thread_structure=thread_structure,
            scenario=scenario_text,
            persona_description=persona_description,
            doc_context=doc_context,
        )

        llm = await self._get_llm()
        raw_content = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.get_system_prompt(doc_context=doc_context),
            temperature=0.8,
            max_tokens=2000,
        )

        # Parse thread
        thread = self.formatter.parse_thread(raw_content, topic=topic)

        # Humanize each tweet with retry
        humanization_applied = False
        total_ai_score = 0.0

        for i, tweet in enumerate(thread.tweets):
            formatted = tweet.content

            for attempt in range(self.humanization_retries + 1):
                is_human_like, report = self.ai_filter.validate_human_likeness(
                    formatted, self.ai_pattern_threshold
                )
                total_ai_score += report.ai_score

                if is_human_like:
                    break

                result = self.persona_writer.humanize_content(formatted, persona_obj)
                formatted = result.transformed
                humanization_applied = True

                if attempt < self.humanization_retries:
                    formatted = self.ai_filter.humanize(formatted)

            tweet.content = formatted

        avg_ai_score = total_ai_score / len(thread.tweets) if thread.tweets else 0.0

        # Format for posting
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
            synthesis_mode=synthesis_mode,
            ai_score=avg_ai_score,
            persona_used=persona_name,
            scenario_used=scenario.category.value if scenario else None,
            humanization_applied=humanization_applied,
        )

    async def analyze_content_for_ai_patterns(
        self,
        content: str,
    ) -> AIPatternReport:
        """Analyze content for AI writing patterns.

        Args:
            content: Content to analyze.

        Returns:
            AIPatternReport with detected patterns.
        """
        return self.ai_filter.analyze(content)

    async def humanize_content(
        self,
        content: str,
        persona: Optional[str] = None,
    ) -> str:
        """Apply humanization to content.

        Args:
            content: Content to humanize.
            persona: Optional persona to use.

        Returns:
            Humanized content.
        """
        persona_obj = None
        if persona:
            persona_obj = self.persona_writer.get_persona(persona)

        result = self.persona_writer.humanize_content(content, persona_obj)
        return result.transformed

    def get_available_synthesis_modes(self) -> list[str]:
        """Get list of available synthesis modes."""
        return [mode.value for mode in SynthesisMode]

    def get_available_personas(self) -> list[str]:
        """Get list of available personas."""
        return self.persona_writer.list_personas()

    def get_available_scenario_categories(self) -> list[str]:
        """Get list of available scenario categories."""
        return [cat.value for cat in self.scenario_generator.get_all_categories()]
