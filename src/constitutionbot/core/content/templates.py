"""Prompt templates for content generation."""

from typing import Optional


class PromptTemplates:
    """Templates for generating prompts for Claude."""

    SYSTEM_PROMPT = """You are a Civic Education Assistant specializing in the Constitution of the Republic of South Africa, 1996.

Your mission is to make constitutional knowledge accessible, engaging, and relevant to all South Africans.

## Core Principles:
1. **Educational Focus**: Explain constitutional concepts clearly without providing legal advice
2. **Accuracy**: Always cite specific sections when discussing constitutional provisions
3. **Accessibility**: Use simple, inclusive language that respects South Africa's multilingual reality
4. **Neutrality**: Present information objectively without political bias
5. **Engagement**: Make content interesting and relevant to everyday life

## Content Guidelines:
- Always reference specific sections (e.g., "Section 9 - Equality")
- Connect constitutional rights to real-world scenarios
- Use examples that resonate with diverse South African audiences
- Include relevant hashtags when creating social media content
- Avoid legal jargon; explain terms when necessary

## Safety Guidelines:
- Never provide specific legal advice for individual situations
- Redirect users to qualified legal professionals for personal legal matters
- Include appropriate disclaimers for sensitive topics
- Flag potentially harmful interpretations or misuse of constitutional provisions

## Output Formats:
- Twitter/X posts: Max 280 characters, engaging, with hashtags
- Threads: Multiple connected tweets, educational narrative
- Scripts: Longer educational content for videos or podcasts

Remember: Your goal is education and civic engagement, not legal consultation."""

    TOPIC_SUGGESTION_PROMPT = """Based on the Constitution of the Republic of South Africa, 1996, suggest an educational topic for a social media post.

Consider:
1. Current relevance to South African society
2. Topics that would engage and educate the public
3. Lesser-known but important constitutional provisions
4. Rights that citizens should be aware of

Provide your response in this format:
TOPIC: [Brief topic title]
SECTION: [Primary section number(s) to reference]
ANGLE: [Suggested educational angle or hook]
WHY: [Brief explanation of why this topic is relevant]"""

    TWEET_GENERATION_PROMPT = """Create an educational tweet about the South African Constitution.

Topic: {topic}

Relevant Constitutional Text:
{context}

Requirements:
- Maximum 280 characters
- Include a citation (e.g., "Section X")
- Make it engaging and educational
- Include 1-2 relevant hashtags
- Do NOT provide legal advice
- Connect to everyday life if possible

Generate only the tweet text, nothing else."""

    THREAD_GENERATION_PROMPT = """Create an educational Twitter thread about the South African Constitution.

Topic: {topic}

Relevant Constitutional Text:
{context}

Requirements:
- Create {num_tweets} connected tweets (280 chars max each)
- Start with a hook that grabs attention
- Each tweet should flow logically to the next
- Include section citations throughout
- End with a takeaway or call to engagement
- Include relevant hashtags in the final tweet
- Do NOT provide legal advice

Format your response as:
TWEET 1: [content]
TWEET 2: [content]
...and so on"""

    REPLY_GENERATION_PROMPT = """You received a question/mention about the South African Constitution:

User @{username} said: "{mention_text}"

Relevant Constitutional Context:
{context}

Generate a helpful, educational reply that:
- Addresses their question or comment
- Cites specific sections when relevant
- Stays under 280 characters
- Is friendly and engaging
- Does NOT provide personal legal advice
- Includes a brief disclaimer if the topic is sensitive

If the question requires legal advice, politely redirect them to seek professional legal counsel.

Generate only the reply text, nothing else."""

    HISTORICAL_ANALYSIS_PROMPT = """Analyze how the South African Constitution relates to this historical event or date:

Event/Date: {event}

Relevant Constitutional Provisions:
{context}

Create educational content that:
1. Briefly explains the historical significance
2. Connects it to relevant constitutional provisions
3. Highlights the constitutional values involved
4. Makes it relevant to today's South Africa

Format: {format_type}
{format_requirements}"""

    SECTION_EXPLAINER_PROMPT = """Explain this section of the South African Constitution in simple terms:

{section_text}

Create an explanation that:
1. Uses everyday language
2. Provides a real-world example
3. Explains why this section matters
4. Is accessible to someone with no legal background

Format: {format_type}
Maximum length: {max_length}"""

    DIALOG_SCRIPT_PROMPT = """Create an educational dialog script about the South African Constitution.

Topic: {topic}

Relevant Constitutional Text:
{context}

Requirements:
- Write a natural conversation between 2-3 characters
- Characters should represent diverse South African perspectives
- One character can ask questions, others explain
- Include specific section citations naturally in the dialog
- Make it educational but engaging and conversational
- Aim for {duration} of spoken content
- Include stage directions in [brackets] where helpful
- End with a clear educational takeaway

Suggested characters:
- A curious citizen asking questions
- A knowledgeable friend, teacher, or community leader explaining
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
    def get_tweet_prompt(
        cls,
        topic: str,
        context: str,
    ) -> str:
        """Get formatted tweet generation prompt."""
        return cls.TWEET_GENERATION_PROMPT.format(
            topic=topic,
            context=context,
        )

    @classmethod
    def get_thread_prompt(
        cls,
        topic: str,
        context: str,
        num_tweets: int = 5,
    ) -> str:
        """Get formatted thread generation prompt."""
        return cls.THREAD_GENERATION_PROMPT.format(
            topic=topic,
            context=context,
            num_tweets=num_tweets,
        )

    @classmethod
    def get_reply_prompt(
        cls,
        username: str,
        mention_text: str,
        context: str,
    ) -> str:
        """Get formatted reply generation prompt."""
        return cls.REPLY_GENERATION_PROMPT.format(
            username=username,
            mention_text=mention_text,
            context=context,
        )

    @classmethod
    def get_historical_prompt(
        cls,
        event: str,
        context: str,
        format_type: str = "tweet",
        format_requirements: str = "Maximum 280 characters with hashtags",
    ) -> str:
        """Get formatted historical analysis prompt."""
        return cls.HISTORICAL_ANALYSIS_PROMPT.format(
            event=event,
            context=context,
            format_type=format_type,
            format_requirements=format_requirements,
        )

    @classmethod
    def get_explainer_prompt(
        cls,
        section_text: str,
        format_type: str = "tweet",
        max_length: str = "280 characters",
    ) -> str:
        """Get formatted section explainer prompt."""
        return cls.SECTION_EXPLAINER_PROMPT.format(
            section_text=section_text,
            format_type=format_type,
            max_length=max_length,
        )

    @classmethod
    def get_script_prompt(
        cls,
        topic: str,
        context: str,
        duration: str = "2-3 minutes",
    ) -> str:
        """Get formatted dialog script generation prompt."""
        return cls.DIALOG_SCRIPT_PROMPT.format(
            topic=topic,
            context=context,
            duration=duration,
        )

    # Chat-specific prompts
    CHAT_SYSTEM_PROMPT = """You are a friendly and knowledgeable Civic Education Assistant specializing in the Constitution of the Republic of South Africa, 1996.

You engage in helpful conversations to:
1. Answer questions about constitutional rights and provisions
2. Explain sections in simple, accessible language
3. Help users explore topics through dialogue
4. Assist with generating educational content (tweets, threads, scripts)

## Conversation Guidelines:
- Be conversational and approachable
- Use clear, simple language
- Always cite specific sections when discussing constitutional provisions (e.g., "Section 9")
- Connect concepts to everyday life and real-world scenarios
- Ask clarifying questions when needed
- Be helpful but never provide specific legal advice

## Response Format:
- Keep responses concise but informative
- Use bullet points for lists
- Cite sections naturally in your responses
- When discussing content generation, explain what you're creating

## Safety:
- Never provide personal legal advice
- Redirect users to qualified legal professionals for specific legal matters
- Be politically neutral
- Include appropriate context for sensitive topics

Remember: You're here to educate and engage, making the Constitution accessible to all South Africans."""

    CHAT_INTENT_DETECTION_PROMPT = """Analyze this user message and determine their intent.

User Message: "{message}"

Previous Context: {context}

Determine:
1. INTENT: What does the user want? (question, generate_content, refine_content, explore_topic, general_chat)
2. TOPIC: What constitutional topic/section is relevant? (if any)
3. CONTENT_TYPE: If generating content, what type? (tweet, thread, script, none)
4. SECTIONS: Which constitutional sections might be relevant? (list section numbers or "none")

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

Constitutional Context:
{context}

Instructions:
1. Address the user's specific feedback
2. Maintain the original format and purpose
3. Keep constitutional accuracy and citations
4. Ensure content remains within format constraints (e.g., 280 chars for tweets)

Generate the refined content:"""

    CHAT_TOPIC_SUGGESTION_PROMPT = """Based on the conversation context and the South African Constitution, suggest 3 engaging topics for educational content.

Conversation Context: {context}

Consider:
1. Topics that build on the current discussion
2. Related but unexplored constitutional provisions
3. Timely or relevant civic education angles

For each suggestion provide:
- Topic title (engaging and clear)
- Primary section(s) to reference
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
    def get_chat_intent_prompt(cls, message: str, context: str) -> str:
        """Get formatted intent detection prompt."""
        return cls.CHAT_INTENT_DETECTION_PROMPT.format(
            message=message,
            context=context or "No previous context",
        )

    @classmethod
    def get_chat_refinement_prompt(
        cls,
        original_content: str,
        content_type: str,
        feedback: str,
        context: str,
    ) -> str:
        """Get formatted content refinement prompt."""
        return cls.CHAT_REFINEMENT_PROMPT.format(
            original_content=original_content,
            content_type=content_type,
            feedback=feedback,
            context=context,
        )

    @classmethod
    def get_chat_topic_suggestions_prompt(cls, context: str) -> str:
        """Get formatted topic suggestions prompt."""
        return cls.CHAT_TOPIC_SUGGESTION_PROMPT.format(
            context=context or "Starting a new conversation about the Constitution",
        )
