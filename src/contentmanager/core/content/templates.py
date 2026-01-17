"""Prompt templates for content generation."""

from typing import Optional

from contentmanager.core.document.models import DocumentContext


# Default context for backward compatibility
DEFAULT_DOCUMENT_CONTEXT = DocumentContext(
    document_name="Constitution of the Republic of South Africa, 1996",
    document_short_name="SA Constitution",
    section_label="Section",
    description="The supreme law of South Africa",
    default_hashtags=["SAConstitution", "KnowYourRights"],
)


class PromptTemplates:
    """Templates for generating prompts for Claude."""

    SYSTEM_PROMPT = """You are a Civic Education Assistant specializing in {document_name}.

Your mission is to make the knowledge in this document accessible, engaging, and relevant to your audience.

## Core Principles:
1. **Educational Focus**: Explain concepts clearly without providing legal advice
2. **Accuracy**: Always cite specific {section_label_lower}s when discussing provisions
3. **Accessibility**: Use simple, inclusive language
4. **Neutrality**: Present information objectively without bias
5. **Engagement**: Make content interesting and relevant to everyday life

## Content Guidelines:
- Always reference specific {section_label_lower}s (e.g., "{section_label} 9")
- Connect provisions to real-world scenarios
- Use examples that resonate with your audience
- Include relevant hashtags when creating social media content
- Avoid jargon; explain terms when necessary

## Safety Guidelines:
- Never provide specific legal advice for individual situations
- Redirect users to qualified professionals for personal matters
- Include appropriate disclaimers for sensitive topics
- Flag potentially harmful interpretations or misuse of provisions

## Output Formats:
- Twitter/X posts: Max 280 characters, engaging, with hashtags
- Threads: Multiple connected tweets, educational narrative
- Scripts: Longer educational content for videos or podcasts

Remember: Your goal is education and civic engagement, not legal or professional consultation."""

    TOPIC_SUGGESTION_PROMPT = """Based on {document_name}, suggest an educational topic for a social media post.

Consider:
1. Current relevance to your audience
2. Topics that would engage and educate the public
3. Lesser-known but important provisions
4. Key rights or concepts that people should be aware of

Provide your response in this format:
TOPIC: [Brief topic title]
{section_label_upper}: [Primary {section_label_lower} number(s) to reference]
ANGLE: [Suggested educational angle or hook]
WHY: [Brief explanation of why this topic is relevant]"""

    TWEET_GENERATION_PROMPT = """Create an educational tweet about {document_short_name}.

Topic: {topic}

Relevant Text from {document_short_name}:
{context}

Requirements:
- Maximum 280 characters
- Include a citation (e.g., "{section_label} X")
- Make it engaging and educational
- Include 1-2 relevant hashtags
- Do NOT provide legal advice
- Connect to everyday life if possible

Generate only the tweet text, nothing else."""

    THREAD_GENERATION_PROMPT = """Create an educational Twitter thread about {document_short_name}.

Topic: {topic}

Relevant Text from {document_short_name}:
{context}

Requirements:
- Create {num_tweets} connected tweets (280 chars max each)
- Start with a hook that grabs attention
- Each tweet should flow logically to the next
- Include {section_label_lower} citations throughout
- End with a takeaway or call to engagement
- Include relevant hashtags in the final tweet
- Do NOT provide legal advice

Format your response as:
TWEET 1: [content]
TWEET 2: [content]
...and so on"""

    REPLY_GENERATION_PROMPT = """You received a question/mention about {document_short_name}:

User @{username} said: "{mention_text}"

Relevant Context from {document_short_name}:
{context}

Generate a helpful, educational reply that:
- Addresses their question or comment
- Cites specific {section_label_lower}s when relevant
- Stays under 280 characters
- Is friendly and engaging
- Does NOT provide personal legal advice
- Includes a brief disclaimer if the topic is sensitive

If the question requires legal advice, politely redirect them to seek professional legal counsel.

Generate only the reply text, nothing else."""

    HISTORICAL_ANALYSIS_PROMPT = """Analyze how {document_short_name} relates to this historical event or date:

Event/Date: {event}

Relevant Provisions from {document_short_name}:
{context}

Create educational content that:
1. Briefly explains the historical significance
2. Connects it to relevant provisions in the document
3. Highlights the values involved
4. Makes it relevant to today's context

Format: {format_type}
{format_requirements}"""

    SECTION_EXPLAINER_PROMPT = """Explain this {section_label_lower} from {document_short_name} in simple terms:

{section_text}

Create an explanation that:
1. Uses everyday language
2. Provides a real-world example
3. Explains why this {section_label_lower} matters
4. Is accessible to someone with no specialized background

Format: {format_type}
Maximum length: {max_length}"""

    DIALOG_SCRIPT_PROMPT = """Create an educational dialog script about {document_short_name}.

Topic: {topic}

Relevant Text from {document_short_name}:
{context}

Requirements:
- Write a natural conversation between 2-3 characters
- Characters should represent diverse perspectives
- One character can ask questions, others explain
- Include specific {section_label_lower} citations naturally in the dialog
- Make it educational but engaging and conversational
- Aim for {duration} of spoken content
- Include stage directions in [brackets] where helpful
- End with a clear educational takeaway

Suggested characters:
- A curious person asking questions
- A knowledgeable friend, teacher, or leader explaining
- Optionally, a third voice adding practical examples

Format your response as:
TITLE: [Script title]
CHARACTERS: [List of characters with brief descriptions]
---
[Character Name]: [Dialog]
[Character Name]: [Dialog]
...
---
TAKEAWAY: [Key lesson from the script]"""

    @classmethod
    def _get_doc_params(cls, doc_context: Optional[DocumentContext] = None) -> dict:
        """Extract template parameters from document context."""
        ctx = doc_context or DEFAULT_DOCUMENT_CONTEXT
        return {
            "document_name": ctx.document_name,
            "document_short_name": ctx.document_short_name,
            "section_label": ctx.section_label,
            "section_label_lower": ctx.section_label.lower(),
            "section_label_upper": ctx.section_label.upper(),
        }

    @classmethod
    def get_system_prompt(
        cls,
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted system prompt with document context."""
        return cls.SYSTEM_PROMPT.format(**cls._get_doc_params(doc_context))

    @classmethod
    def get_topic_suggestion_prompt(
        cls,
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted topic suggestion prompt with document context."""
        return cls.TOPIC_SUGGESTION_PROMPT.format(**cls._get_doc_params(doc_context))

    @classmethod
    def get_tweet_prompt(
        cls,
        topic: str,
        context: str,
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted tweet generation prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.TWEET_GENERATION_PROMPT.format(
            topic=topic,
            context=context,
            **params,
        )

    @classmethod
    def get_thread_prompt(
        cls,
        topic: str,
        context: str,
        num_tweets: int = 5,
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted thread generation prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.THREAD_GENERATION_PROMPT.format(
            topic=topic,
            context=context,
            num_tweets=num_tweets,
            **params,
        )

    @classmethod
    def get_reply_prompt(
        cls,
        username: str,
        mention_text: str,
        context: str,
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted reply generation prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.REPLY_GENERATION_PROMPT.format(
            username=username,
            mention_text=mention_text,
            context=context,
            **params,
        )

    @classmethod
    def get_historical_prompt(
        cls,
        event: str,
        context: str,
        format_type: str = "tweet",
        format_requirements: str = "Maximum 280 characters with hashtags",
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted historical analysis prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.HISTORICAL_ANALYSIS_PROMPT.format(
            event=event,
            context=context,
            format_type=format_type,
            format_requirements=format_requirements,
            **params,
        )

    @classmethod
    def get_explainer_prompt(
        cls,
        section_text: str,
        format_type: str = "tweet",
        max_length: str = "280 characters",
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted section explainer prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.SECTION_EXPLAINER_PROMPT.format(
            section_text=section_text,
            format_type=format_type,
            max_length=max_length,
            **params,
        )

    @classmethod
    def get_script_prompt(
        cls,
        topic: str,
        context: str,
        duration: str = "2-3 minutes",
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted dialog script generation prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.DIALOG_SCRIPT_PROMPT.format(
            topic=topic,
            context=context,
            duration=duration,
            **params,
        )

    # Chat-specific prompts
    CHAT_SYSTEM_PROMPT = """You are a friendly and knowledgeable Civic Education Assistant specializing in {document_name}.

You engage in helpful conversations to:
1. Answer questions about the provisions and concepts in this document
2. Explain {section_label_lower}s in simple, accessible language
3. Help users explore topics through dialogue
4. Assist with generating educational content (tweets, threads, scripts)

## Conversation Guidelines:
- Be conversational and approachable
- Use clear, simple language
- Always cite specific {section_label_lower}s when discussing provisions (e.g., "{section_label} 9")
- Connect concepts to everyday life and real-world scenarios
- Ask clarifying questions when needed
- Be helpful but never provide specific legal advice

## Response Format:
- Keep responses concise but informative
- Use bullet points for lists
- Cite {section_label_lower}s naturally in your responses
- When discussing content generation, explain what you're creating

## Safety:
- Never provide personal legal advice
- Redirect users to qualified professionals for specific matters
- Be politically neutral
- Include appropriate context for sensitive topics

Remember: You're here to educate and engage, making {document_short_name} accessible to everyone."""

    CHAT_INTENT_DETECTION_PROMPT = """Analyze this user message and determine their intent.

User Message: "{message}"

Previous Context: {context}

Document: {document_short_name}

Determine:
1. INTENT: What does the user want? (question, generate_content, refine_content, explore_topic, general_chat)
2. TOPIC: What topic/{section_label_lower} is relevant? (if any)
3. CONTENT_TYPE: If generating content, what type? (tweet, thread, script, none)
4. SECTIONS: Which {section_label_lower}s might be relevant? (list numbers or "none")

Response format (JSON):
{{
    "intent": "question|generate_content|refine_content|explore_topic|general_chat",
    "topic": "extracted topic or null",
    "content_type": "tweet|thread|script|none",
    "sections": [section_numbers] or [],
    "confidence": 0.0-1.0
}}"""

    CHAT_REFINEMENT_PROMPT = """Refine the following content based on user feedback.

Original Content:
{original_content}

Content Type: {content_type}

User Feedback: {feedback}

Context from {document_short_name}:
{context}

Instructions:
1. Address the user's specific feedback
2. Maintain the original format and purpose
3. Keep accuracy and {section_label_lower} citations
4. Ensure content remains within format constraints (e.g., 280 chars for tweets)

Generate the refined content:"""

    CHAT_TOPIC_SUGGESTION_PROMPT = """Based on the conversation context and {document_short_name}, suggest 3 engaging topics for educational content.

Conversation Context: {context}

Consider:
1. Topics that build on the current discussion
2. Related but unexplored provisions in the document
3. Timely or relevant civic education angles

For each suggestion provide:
- Topic title (engaging and clear)
- Primary {section_label_lower}(s) to reference
- Brief angle/hook for the content
- Why this would be valuable to explore

Format as JSON array:
[
    {{
        "title": "topic title",
        "sections": [section_numbers],
        "angle": "hook or angle",
        "reason": "why this is valuable"
    }}
]"""

    @classmethod
    def get_chat_system_prompt(
        cls,
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted chat system prompt with document context."""
        return cls.CHAT_SYSTEM_PROMPT.format(**cls._get_doc_params(doc_context))

    @classmethod
    def get_chat_intent_prompt(
        cls,
        message: str,
        context: str,
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted intent detection prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.CHAT_INTENT_DETECTION_PROMPT.format(
            message=message,
            context=context or "No previous context",
            **params,
        )

    @classmethod
    def get_chat_refinement_prompt(
        cls,
        original_content: str,
        content_type: str,
        feedback: str,
        context: str,
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted content refinement prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.CHAT_REFINEMENT_PROMPT.format(
            original_content=original_content,
            content_type=content_type,
            feedback=feedback,
            context=context,
            **params,
        )

    @classmethod
    def get_chat_topic_suggestions_prompt(
        cls,
        context: str,
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted topic suggestions prompt."""
        params = cls._get_doc_params(doc_context)
        ctx = doc_context or DEFAULT_DOCUMENT_CONTEXT
        return cls.CHAT_TOPIC_SUGGESTION_PROMPT.format(
            context=context or f"Starting a new conversation about {ctx.document_short_name}",
            **params,
        )

    # ========================================================================
    # SYNTHESIS PROMPTS - For intelligent content synthesis system
    # ========================================================================

    INSIGHT_EXTRACTION_PROMPT = """Analyze this provision from {document_short_name} deeply:

{section_text}

Extract the following insights:

1. CORE PRINCIPLE: What fundamental idea does this protect or establish?
   - What value or right is at the heart of this provision?
   - Why would the framers have included this?

2. PRACTICAL MEANING: How does this affect someone's daily life?
   - Give a concrete example of when this matters
   - Who benefits from this provision and how?

3. COMMON MISCONCEPTION: What do people often get wrong about this?
   - What's the gap between public perception and reality?
   - What nuance do people miss?

4. TENSION: What competing values does this balance?
   - What's the trade-off inherent in this provision?
   - When might this provision conflict with other rights or interests?

5. ANALOGY: Compare this to something everyone understands
   - Use everyday scenarios or objects
   - Make the abstract concrete

Format your response as JSON:
{{
    "core_principle": "...",
    "practical_meaning": "...",
    "common_misconception": "...",
    "tension": "...",
    "analogy": "...",
    "keywords": ["...", "..."]
}}"""

    SYNTHESIS_PROMPT = """Given these insights about {topic}:

{insights}

Create original commentary that:
1. Offers a fresh perspective not immediately obvious from the text
2. Connects to everyday experience in {scenario_category}
3. Challenges a common assumption OR reveals a hidden implication
4. Uses concrete, specific language (not abstract generalities)

Synthesis Mode: {mode}
Voice: {persona_description}

== CRITICAL: DO NOT ==
- Start with "It's important to note", "In today's world", or similar AI cliches
- Use words like "delve", "unpack", "robust", "leverage", "foster", "empower"
- Structure as "First... Second... Third..." or "Firstly... Secondly..."
- End with a generic call to action like "What do you think?" or "Share your thoughts"
- Use phrases like "plays a crucial role" or "serves as a reminder"

== INSTEAD, DO ==
- Start mid-thought or with a specific observation
- Use contractions naturally ("it's", "don't", "they're")
- Include one slightly imperfect element (dash, parenthetical, sentence fragment)
- End with a thought-provoking angle, not a summary
- Sound like a thoughtful person sharing an insight, not a press release

{additional_guidance}

Output only the synthesized content, nothing else."""

    HUMANIZATION_PROMPT = """Rewrite this content to sound more natural and human:

Original: {content}

Transform it by:
1. Varying sentence lengths (mix short punchy with longer flowing)
2. Using contractions where natural
3. Adding one slightly imperfect element (dash, parenthetical, fragment)
4. Starting differently than "This" or "The" or "It's important"
5. Avoiding list structures unless truly necessary
6. Replacing any corporate-speak with everyday words

The content should sound like a real person wrote it while having coffee with a friend.

Voice guidance: {persona_description}

Output only the rewritten content, nothing else."""

    TWEET_SYNTHESIS_PROMPT = """Create an educational tweet about {topic} from {document_short_name}.

Insight to convey:
{insight_context}

Scenario context:
{scenario}

== FORMAT REQUIREMENTS ==
- Maximum 280 characters
- Must include a citation (e.g., "{section_label} X")
- Include 1 relevant hashtag maximum
- NO legal advice

== WRITING STYLE ==
Voice: {persona_description}

Opening style (choose one that fits):
- Start with a specific observation
- Open with a brief scenario
- Lead with a surprising angle
- Begin with what most people miss

DO NOT:
- Start with "Did you know" or "It's important to note"
- Use words like "delve", "unpack", "robust"
- End with "What do you think?" or "Share your thoughts"

DO:
- Sound like an interesting person sharing an insight
- Use contractions naturally
- Be specific rather than general
- Make it memorable

Generate only the tweet text, nothing else."""

    THREAD_SYNTHESIS_PROMPT = """Create an educational Twitter thread about {topic} from {document_short_name}.

Insights to convey:
{insight_context}

Scenario context:
{scenario}

Thread structure: {thread_structure}

== FORMAT REQUIREMENTS ==
- Create {num_tweets} connected tweets (280 chars max each)
- Include {section_label_lower} citations throughout
- Include relevant hashtags only in the final tweet
- NO legal advice

== WRITING STYLE ==
Voice: {persona_description}

Thread flow:
1. Hook that grabs attention (NOT "Thread:" or "Did you know")
2. Build understanding progressively
3. Each tweet should flow naturally to the next
4. End with insight that stays with the reader

DO NOT:
- Number tweets as "1/5", "2/5" (let the thread stand alone)
- Use "Let's dive in" or "Let's unpack this"
- Structure as "First... Second... Third..."
- End with generic engagement bait

DO:
- Open with something specific and interesting
- Use transitions that feel natural
- Vary sentence length within and across tweets
- End with something worth thinking about

Format your response as:
TWEET 1: [content]
TWEET 2: [content]
...and so on"""

    @classmethod
    def get_insight_extraction_prompt(
        cls,
        section_text: str,
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted insight extraction prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.INSIGHT_EXTRACTION_PROMPT.format(
            section_text=section_text,
            **params,
        )

    @classmethod
    def get_synthesis_prompt(
        cls,
        topic: str,
        insights: str,
        mode: str = "CHALLENGE",
        scenario_category: str = "daily life",
        persona_description: str = "conversational and thoughtful",
        additional_guidance: str = "",
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted synthesis prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.SYNTHESIS_PROMPT.format(
            topic=topic,
            insights=insights,
            mode=mode,
            scenario_category=scenario_category,
            persona_description=persona_description,
            additional_guidance=additional_guidance,
            **params,
        )

    @classmethod
    def get_humanization_prompt(
        cls,
        content: str,
        persona_description: str = "conversational and natural",
    ) -> str:
        """Get formatted humanization prompt."""
        return cls.HUMANIZATION_PROMPT.format(
            content=content,
            persona_description=persona_description,
        )

    @classmethod
    def get_tweet_synthesis_prompt(
        cls,
        topic: str,
        insight_context: str,
        scenario: str = "",
        persona_description: str = "conversational",
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted tweet synthesis prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.TWEET_SYNTHESIS_PROMPT.format(
            topic=topic,
            insight_context=insight_context,
            scenario=scenario or "everyday situations",
            persona_description=persona_description,
            **params,
        )

    @classmethod
    def get_thread_synthesis_prompt(
        cls,
        topic: str,
        insight_context: str,
        num_tweets: int = 5,
        thread_structure: str = "progressive revelation",
        scenario: str = "",
        persona_description: str = "conversational",
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted thread synthesis prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.THREAD_SYNTHESIS_PROMPT.format(
            topic=topic,
            insight_context=insight_context,
            num_tweets=num_tweets,
            thread_structure=thread_structure,
            scenario=scenario or "everyday situations",
            persona_description=persona_description,
            **params,
        )
