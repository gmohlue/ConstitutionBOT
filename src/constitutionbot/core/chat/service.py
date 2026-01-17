"""Chat service for interactive conversations about the Constitution."""

import json
import re
from dataclasses import dataclass
from typing import Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.core.claude_client import ClaudeClient, get_claude_client
from constitutionbot.core.constitution.retriever import ConstitutionRetriever
from constitutionbot.core.content.generator import ContentGenerator, GeneratedContent
from constitutionbot.core.content.templates import PromptTemplates
from constitutionbot.core.llm import LLMProvider, get_llm_provider
from constitutionbot.database.models import (
    ConversationMessage,
    MessageRole,
    MessageType,
)
from constitutionbot.database.repositories.conversation import (
    ConversationRepository,
    MessageRepository,
)


@dataclass
class DetectedIntent:
    """Result of intent detection."""

    intent: str  # question, generate_content, refine_content, explore_topic, general_chat
    topic: Optional[str] = None
    content_type: Optional[str] = None  # tweet, thread, script
    sections: Optional[list[int]] = None
    confidence: float = 0.0


@dataclass
class TopicSuggestion:
    """A suggested topic for content generation."""

    title: str
    sections: list[int]
    angle: str
    reason: str


@dataclass
class ChatResponse:
    """Response from the chat service."""

    content: str
    message_type: str = MessageType.TEXT.value
    structured_data: Optional[dict] = None
    citations: Optional[list[dict]] = None


class ChatService:
    """Service for handling chat interactions."""

    def __init__(
        self,
        session: AsyncSession,
        llm_provider: Optional[Union[LLMProvider, ClaudeClient]] = None,
        claude_client: Optional[ClaudeClient] = None,  # Deprecated, for backward compat
    ):
        self.session = session
        self._llm_provider = llm_provider or claude_client
        self._llm_initialized = False
        self.retriever = ConstitutionRetriever(session)
        self.generator = ContentGenerator(session, llm_provider=self._llm_provider)
        self.conversation_repo = ConversationRepository(session)
        self.message_repo = MessageRepository(session)

    async def _get_llm(self) -> Union[LLMProvider, ClaudeClient]:
        """Get the LLM provider, initializing if needed."""
        if self._llm_provider is not None:
            return self._llm_provider
        if not self._llm_initialized:
            self._llm_provider = await get_llm_provider(self.session)
            self._llm_initialized = True
            # Update generator's LLM provider
            self.generator._llm_provider = self._llm_provider
        return self._llm_provider

    @property
    def claude(self) -> Union[LLMProvider, ClaudeClient]:
        """Backward compatibility property. Use _get_llm() for async contexts."""
        if self._llm_provider is None:
            self._llm_provider = get_claude_client()
        return self._llm_provider

    async def process_message(
        self,
        conversation_id: int,
        user_message: str,
        action: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> ChatResponse:
        """Process a user message and generate a response.

        Args:
            conversation_id: The conversation ID
            user_message: The user's message
            action: Optional explicit action (generate, refine, suggest_topics)
            parameters: Optional parameters for the action

        Returns:
            ChatResponse with the assistant's response
        """
        parameters = parameters or {}

        # Handle explicit actions
        if action == "suggest_topics":
            return await self._handle_suggest_topics(conversation_id)
        elif action == "generate":
            content_type = parameters.get("content_type", "tweet")
            topic = parameters.get("topic") or user_message
            return await self._handle_generate(conversation_id, topic, content_type)
        elif action == "refine":
            message_id = parameters.get("message_id")
            if message_id:
                return await self._handle_refine(
                    conversation_id, message_id, user_message
                )

        # Auto-detect intent from message
        context = await self.build_conversation_context(conversation_id, max_messages=5)
        intent = await self.detect_intent(user_message, context)

        # Route based on detected intent
        if intent.intent == "generate_content" and intent.topic:
            content_type = intent.content_type or "tweet"
            return await self._handle_generate(
                conversation_id, intent.topic, content_type, intent.sections
            )
        elif intent.intent == "question":
            return await self._handle_question(
                conversation_id, user_message, intent.topic, intent.sections
            )
        elif intent.intent == "explore_topic" and intent.topic:
            return await self._handle_explore(
                conversation_id, intent.topic, intent.sections
            )
        else:
            # General conversational response
            return await self._handle_general_chat(conversation_id, user_message, context)

    async def detect_intent(
        self,
        message: str,
        context: str,
    ) -> DetectedIntent:
        """Detect the user's intent from their message.

        Args:
            message: The user's message
            context: Previous conversation context

        Returns:
            DetectedIntent with the detected intent and parameters
        """
        # Quick pattern matching for common intents
        message_lower = message.lower()

        # Check for explicit generation requests
        generate_patterns = [
            r"(generate|create|make|write)\s+(a\s+)?(tweet|thread|script)",
            r"(tweet|thread|script)\s+(about|on|for)",
            r"make this a (tweet|thread|script)",
        ]
        for pattern in generate_patterns:
            match = re.search(pattern, message_lower)
            if match:
                content_type = "tweet"
                if "thread" in match.group(0):
                    content_type = "thread"
                elif "script" in match.group(0):
                    content_type = "script"
                return DetectedIntent(
                    intent="generate_content",
                    topic=message,
                    content_type=content_type,
                    confidence=0.9,
                )

        # Check for refinement requests
        refine_patterns = [
            r"(make it|change|modify|adjust|refine|edit)",
            r"(shorter|longer|more|less|add|remove)",
            r"(focus on|emphasize|highlight)",
        ]
        for pattern in refine_patterns:
            if re.search(pattern, message_lower):
                return DetectedIntent(
                    intent="refine_content",
                    confidence=0.8,
                )

        # Check for questions
        question_patterns = [
            r"^(what|who|where|when|why|how|which|can|do|does|is|are|will|would|could|should)",
            r"\?$",
            r"(tell me|explain|describe|help me understand)",
        ]
        for pattern in question_patterns:
            if re.search(pattern, message_lower):
                return DetectedIntent(
                    intent="question",
                    topic=message,
                    confidence=0.85,
                )

        # Use LLM for more complex intent detection
        try:
            prompt = PromptTemplates.get_chat_intent_prompt(message, context)
            llm = await self._get_llm()
            response = llm.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=200,
            )

            # Parse JSON response
            json_match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return DetectedIntent(
                    intent=data.get("intent", "general_chat"),
                    topic=data.get("topic"),
                    content_type=data.get("content_type"),
                    sections=data.get("sections", []),
                    confidence=data.get("confidence", 0.5),
                )
        except (json.JSONDecodeError, Exception):
            pass

        # Default to general chat
        return DetectedIntent(intent="general_chat", confidence=0.5)

    async def answer_question(
        self,
        question: str,
        context: str,
        sections: Optional[list[int]] = None,
    ) -> tuple[str, list[dict]]:
        """Answer a question about the Constitution.

        Args:
            question: The user's question
            context: Previous conversation context
            sections: Specific sections to reference

        Returns:
            Tuple of (response text, citations list)
        """
        # Get relevant sections
        if sections:
            constitution_sections = []
            for num in sections[:5]:
                section = await self.retriever.get_section(num)
                if section:
                    constitution_sections.append(section)
        else:
            constitution_sections = await self.retriever.get_sections_for_topic(
                question, limit=3
            )

        # Build constitutional context
        const_context = ""
        citations = []
        if constitution_sections:
            const_context = await self.retriever.format_multiple_sections(
                constitution_sections
            )
            for section in constitution_sections:
                citations.append({
                    "section_num": section.section_num,
                    "section_title": section.section_title,
                    "chapter_num": section.chapter_num,
                    "chapter_title": section.chapter_title,
                })

        # Build messages for conversation
        messages = []
        if context:
            # Add context as previous exchange
            messages.append({"role": "user", "content": "Previous context:\n" + context})
            messages.append({"role": "assistant", "content": "I understand the context."})

        full_question = question
        if const_context:
            full_question = f"""Based on these relevant constitutional provisions:

{const_context}

---

Question: {question}

Please answer this question about the South African Constitution. Cite specific sections where relevant."""

        messages.append({"role": "user", "content": full_question})

        llm = await self._get_llm()
        response = llm.generate_with_messages(
            messages=messages,
            system_prompt=PromptTemplates.CHAT_SYSTEM_PROMPT,
            temperature=0.7,
        )

        return response, citations

    async def suggest_topics(
        self,
        context: str,
        count: int = 3,
    ) -> list[TopicSuggestion]:
        """Suggest topics for content generation.

        Args:
            context: Previous conversation context
            count: Number of suggestions to return

        Returns:
            List of TopicSuggestion objects
        """
        prompt = PromptTemplates.get_chat_topic_suggestions_prompt(context)
        llm = await self._get_llm()
        response = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            temperature=0.8,
            max_tokens=800,
        )

        suggestions = []
        try:
            # Find JSON array in response
            json_match = re.search(r"\[[\s\S]*\]", response)
            if json_match:
                data = json.loads(json_match.group())
                for item in data[:count]:
                    suggestions.append(TopicSuggestion(
                        title=item.get("title", ""),
                        sections=item.get("sections", []),
                        angle=item.get("angle", ""),
                        reason=item.get("reason", ""),
                    ))
        except (json.JSONDecodeError, Exception):
            # Fallback: generate a default suggestion
            suggestions.append(TopicSuggestion(
                title="Your Right to Equality",
                sections=[9],
                angle="How Section 9 protects everyone from discrimination",
                reason="Equality is a foundational right in our Constitution",
            ))

        return suggestions

    async def generate_content(
        self,
        topic: str,
        content_type: str,
        context: str,
        sections: Optional[list[int]] = None,
    ) -> GeneratedContent:
        """Generate content for the given topic.

        Args:
            topic: The topic to generate content about
            content_type: Type of content (tweet, thread, script)
            context: Previous conversation context
            sections: Specific sections to reference

        Returns:
            GeneratedContent object
        """
        if content_type == "thread":
            return await self.generator.generate_thread(
                topic=topic,
                mode="user_provided",
                section_nums=sections,
            )
        elif content_type == "script":
            return await self.generator.generate_script(
                topic=topic,
                mode="user_provided",
                section_nums=sections,
            )
        else:
            return await self.generator.generate_tweet(
                topic=topic,
                mode="user_provided",
                section_nums=sections,
            )

    async def refine_content(
        self,
        original_content: str,
        content_type: str,
        feedback: str,
        context: str,
    ) -> str:
        """Refine content based on user feedback.

        Args:
            original_content: The original generated content
            content_type: Type of content
            feedback: User's refinement feedback
            context: Conversation context

        Returns:
            Refined content string
        """
        # Get relevant constitutional context
        sections = await self.retriever.get_sections_for_topic(original_content, limit=3)
        const_context = ""
        if sections:
            const_context = await self.retriever.format_multiple_sections(sections)

        prompt = PromptTemplates.get_chat_refinement_prompt(
            original_content=original_content,
            content_type=content_type,
            feedback=feedback,
            context=const_context,
        )

        llm = await self._get_llm()
        response = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            temperature=0.6,
        )

        return response.strip()

    async def build_conversation_context(
        self,
        conversation_id: int,
        max_messages: int = 10,
    ) -> str:
        """Build a context string from recent conversation messages.

        Args:
            conversation_id: The conversation ID
            max_messages: Maximum number of messages to include

        Returns:
            Formatted context string
        """
        messages = await self.message_repo.get_last_n_messages(
            conversation_id, n=max_messages
        )

        if not messages:
            return ""

        context_parts = []
        for msg in messages:
            role = "User" if msg.role == MessageRole.USER.value else "Assistant"
            context_parts.append(f"{role}: {msg.content[:500]}")

        return "\n".join(context_parts)

    async def _handle_suggest_topics(self, conversation_id: int) -> ChatResponse:
        """Handle a request for topic suggestions."""
        context = await self.build_conversation_context(conversation_id, max_messages=3)
        suggestions = await self.suggest_topics(context)

        # Format suggestions for display
        response_parts = ["Here are some topics you might find interesting:\n"]
        structured_data = {"suggestions": []}

        for i, suggestion in enumerate(suggestions, 1):
            response_parts.append(
                f"{i}. **{suggestion.title}**\n"
                f"   *{suggestion.angle}*\n"
                f"   Sections: {', '.join(str(s) for s in suggestion.sections)}"
            )
            structured_data["suggestions"].append({
                "title": suggestion.title,
                "sections": suggestion.sections,
                "angle": suggestion.angle,
                "reason": suggestion.reason,
            })

        response_parts.append(
            "\nClick on a topic or tell me what you'd like to explore!"
        )

        return ChatResponse(
            content="\n".join(response_parts),
            message_type=MessageType.TOPIC_SUGGESTION.value,
            structured_data=structured_data,
        )

    async def _handle_generate(
        self,
        conversation_id: int,
        topic: str,
        content_type: str,
        sections: Optional[list[int]] = None,
    ) -> ChatResponse:
        """Handle a content generation request."""
        context = await self.build_conversation_context(conversation_id, max_messages=3)

        generated = await self.generate_content(
            topic=topic,
            content_type=content_type,
            context=context,
            sections=sections,
        )

        # Build response
        type_name = {
            "tweet": "tweet",
            "thread": "thread",
            "script": "dialog script",
        }.get(content_type, "content")

        response = f"Here's a {type_name} about {topic}:\n\n{generated.formatted_content}"

        if generated.validation and not generated.validation.is_valid:
            response += f"\n\n*Note: {', '.join(generated.validation.warnings)}*"

        return ChatResponse(
            content=response,
            message_type=MessageType.GENERATED_CONTENT.value,
            structured_data={
                "content_type": content_type,
                "topic": topic,
                "raw_content": generated.raw_content,
                "formatted_content": generated.formatted_content,
            },
            citations=generated.citations,
        )

    async def _handle_question(
        self,
        conversation_id: int,
        question: str,
        topic: Optional[str],
        sections: Optional[list[int]],
    ) -> ChatResponse:
        """Handle a question about the Constitution."""
        context = await self.build_conversation_context(conversation_id, max_messages=5)

        response, citations = await self.answer_question(
            question=question,
            context=context,
            sections=sections,
        )

        return ChatResponse(
            content=response,
            message_type=MessageType.TEXT.value,
            citations=citations,
        )

    async def _handle_explore(
        self,
        conversation_id: int,
        topic: str,
        sections: Optional[list[int]],
    ) -> ChatResponse:
        """Handle a request to explore a topic."""
        # Get relevant sections
        if sections:
            constitution_sections = []
            for num in sections[:5]:
                section = await self.retriever.get_section(num)
                if section:
                    constitution_sections.append(section)
        else:
            constitution_sections = await self.retriever.get_sections_for_topic(
                topic, limit=3
            )

        if not constitution_sections:
            return ChatResponse(
                content=f"I couldn't find specific sections related to '{topic}'. "
                "Could you tell me more about what aspect of the Constitution you'd like to explore?",
                message_type=MessageType.TEXT.value,
            )

        # Build an exploratory response
        const_context = await self.retriever.format_multiple_sections(constitution_sections)

        prompt = f"""The user wants to explore the topic: "{topic}"

Here are the relevant constitutional provisions:

{const_context}

Provide an engaging overview of this topic that:
1. Explains the key provisions in simple terms
2. Gives a real-world example of how these rights apply
3. Suggests related topics they might want to explore
4. Offers to generate content (tweet, thread, or script) about any aspect"""

        llm = await self._get_llm()
        response = llm.generate(
            prompt=prompt,
            system_prompt=PromptTemplates.CHAT_SYSTEM_PROMPT,
            temperature=0.7,
        )

        citations = [
            {
                "section_num": s.section_num,
                "section_title": s.section_title,
                "chapter_num": s.chapter_num,
                "chapter_title": s.chapter_title,
            }
            for s in constitution_sections
        ]

        return ChatResponse(
            content=response,
            message_type=MessageType.TEXT.value,
            citations=citations,
        )

    async def _handle_refine(
        self,
        conversation_id: int,
        message_id: int,
        feedback: str,
    ) -> ChatResponse:
        """Handle a content refinement request."""
        # Get the original message
        original_message = await self.message_repo.get_by_id(message_id)
        if not original_message or not original_message.structured_data:
            return ChatResponse(
                content="I couldn't find the content to refine. "
                "Could you tell me what changes you'd like?",
                message_type=MessageType.TEXT.value,
            )

        original_content = original_message.structured_data.get("formatted_content", "")
        content_type = original_message.structured_data.get("content_type", "tweet")
        topic = original_message.structured_data.get("topic", "")

        context = await self.build_conversation_context(conversation_id, max_messages=3)

        refined = await self.refine_content(
            original_content=original_content,
            content_type=content_type,
            feedback=feedback,
            context=context,
        )

        response = f"Here's the refined {content_type}:\n\n{refined}"

        return ChatResponse(
            content=response,
            message_type=MessageType.GENERATED_CONTENT.value,
            structured_data={
                "content_type": content_type,
                "topic": topic,
                "formatted_content": refined,
                "original_message_id": message_id,
            },
            citations=original_message.citations,
        )

    async def _handle_general_chat(
        self,
        conversation_id: int,
        message: str,
        context: str,
    ) -> ChatResponse:
        """Handle general conversational messages."""
        messages = []

        if context:
            # Parse context into message format
            for line in context.split("\n"):
                if line.startswith("User: "):
                    messages.append({
                        "role": "user",
                        "content": line[6:],
                    })
                elif line.startswith("Assistant: "):
                    messages.append({
                        "role": "assistant",
                        "content": line[11:],
                    })

        messages.append({"role": "user", "content": message})

        llm = await self._get_llm()
        response = llm.generate_with_messages(
            messages=messages,
            system_prompt=PromptTemplates.CHAT_SYSTEM_PROMPT,
            temperature=0.7,
        )

        return ChatResponse(
            content=response,
            message_type=MessageType.TEXT.value,
        )
