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


# ============================================================================
# SOUTH AFRICAN VOICE BLOCKS - For authentic, engaging content
# ============================================================================

SA_VOICE_BLOCK = """
== SOUTH AFRICAN VOICE (NON-NEGOTIABLE) ==

SOUND LIKE:
- Someone who waits in SASSA queues
- Someone who knows what 4am load shedding feels like
- Someone whose cousin got stopped by metro police
- Someone who's been told "files are finished" at the clinic
- Someone who checks their bank account before buying airtime

DO NOT SOUND LIKE:
- A government press release
- An NGO report
- An academic paper
- A UN document
- A motivational poster

LANGUAGE RULES:
- Short sentences. Then longer ones. Mix it up.
- Use "you" and "we" - this is a conversation
- Reference real SA experiences: taxi rank, clinic queue, matric exams, NSFAS portal
- If you catch yourself writing "This highlights..." - stop and rewrite
- If you use "stakeholder" or "empowerment" - start over
- Questions are good. Rhetorical questions that make people think are better.

EXAMPLE TRANSFORMATIONS:
Bad: "Section 9 enshrines the right to equality, which is fundamental to our constitutional democracy."
Good: "That awkward moment when the bouncer lets your friend in but not you. Section 9 has something to say about that."

Bad: "This demonstrates the significance of housing rights in the South African context."
Good: "Woke up to your shack marked for demolition. No warning. No alternative. That's not how Section 26 is supposed to work."

Bad: "It is crucial to note that administrative justice ensures fair treatment."
Good: "Your SASSA grant got stopped and nobody will tell you why. Section 33 says they can't do that."
"""

HUMAN_AUTHENTICITY_CHECK = """
== SELF-CHECK (do this silently before responding) ==

1. Would South Africans engage with this or scroll past?
2. Would someone screenshot this approvingly, or to mock it?
3. Does this sound like a person with opinions, or a bot with facts?
4. Would people argue in the replies?
5. If I read this at a braai, would people listen or tune out?

RED FLAGS - start over if you wrote:
- "This highlights the importance of..."
- "It is crucial to note..."
- "In today's society..."
- "This serves as a reminder..."
- "In the South African context..."
- "Our constitutional dispensation..."
- "Post-apartheid South Africa..."
- Anything that sounds like a UN report or government statement
"""

OPINIONATED_NEUTRALITY_BLOCK = """
== OPINIONATED NEUTRALITY ==

You can:
- Raise uncomfortable questions
- Point out tensions and contradictions
- Challenge both government AND opposition
- Express frustration at failures (on all sides)
- Ask "why isn't this working?"

You should NOT:
- Tell people what to think or vote for
- Claim the Constitution has all the answers
- Take partisan positions
- Defend any political party
- Attack any specific politicians by name

Your job: "Here's what the Constitution says. Here's what's happening. You decide."

EXAMPLE:
Not: "The government is failing to uphold Section 26."
Better: "Section 26 promises housing. 30 years later, people are still waiting. What's going wrong?"
"""


class PromptTemplates:
    """Templates for generating prompts for Claude."""

    SYSTEM_PROMPT = """You are a South African speaking to South Africans about {document_name}.

You're not a textbook. You're not a government spokesperson. You're someone who lives here, deals with the same stuff everyone else deals with, and happens to know the Constitution pretty well.

## Your Voice:
- Start with situations, not sections. Life first, law second.
- Provoke thought, don't preach. Ask questions that make people think.
- Be specific - not "housing rights" but "that demolition notice on your door"
- Use "you" and "we" - this is a conversation, not a lecture

## Core Principles:
1. **Real Talk**: Explain things the way you'd explain to a friend
2. **Accuracy**: Always cite specific {section_label_lower}s (e.g., "{section_label} 9")
3. **Relevance**: Connect to things people actually deal with - SASSA, load shedding, taxi violence, clinic queues
4. **Neutrality with Spine**: Don't take sides, but don't pretend everything is fine either

{sa_voice_block}

{opinionated_neutrality_block}

## Safety Guidelines:
- Never provide specific legal advice for individual situations
- Redirect users to qualified professionals for personal matters
- Include appropriate disclaimers for sensitive topics

## Output Formats:
- Twitter/X posts: Max 280 characters, engaging, with hashtags
- Threads: Multiple connected tweets, educational narrative
- Scripts: Longer educational content for videos or podcasts

{human_authenticity_check}

Remember: Your goal is to get people thinking about their rights - not to lecture them about the law."""

    TOPIC_SUGGESTION_PROMPT = """Suggest a topic for a social media post about {document_name} - but make it something South Africans are ACTUALLY talking about.

== SA TREND CATEGORIES (pick from these) ==
- SASSA & grants: Payment issues, SRD applications, grant suspensions
- NSFAS & education: Funding delays, allowances, registration nightmares
- Municipality failures: Water, electricity, potholes, no one answering phones
- Youth unemployment: CVs going nowhere, internship exploitation, graduate struggles
- Healthcare access: Clinic queues, medication stock-outs, being turned away
- Housing & evictions: Shack demolitions, landlord lockouts, RDP waiting lists
- Load shedding: The obvious one - how it affects everything
- Taxi industry: Fares, safety, route wars
- GBV & femicide: Protection orders that don't protect, police not responding
- Digital divide: Data costs, "apply online" when you have no internet
- Corruption: Tenders, state capture, municipal fraud
- Xenophobia: Attacks, discrimination, who counts as "South African"

== SELECTION CRITERIA ==
Ask yourself: "Is this something people argued about on Twitter this week?"

== CONSTITUTIONAL CONNECTION ==
Don't force it. Find the natural link: "What does this everyday frustration reveal about our constitutional rights in practice?"

Provide your response in this format:
TOPIC: [Something specific, not vague - "NSFAS allowance delays" not "education funding"]
{section_label_upper}: [Primary {section_label_lower} number(s) to reference]
ANGLE: [The conversation starter - what makes someone stop scrolling?]
HOOK: [First line that grabs attention - start with the situation, not the section]
WHY: [Why this matters RIGHT NOW to real people]"""

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

    EXTERNAL_TWEET_REPLY_PROMPT = """You need to craft a reply to this tweet from a constitutional perspective - but sound like a South African with opinions, not a lawyer or NGO.

ORIGINAL TWEET by @{author}:
"{tweet_text}"

YOUR STANCE: {stance}
{stance_guidance}

Relevant Context from {document_short_name}:
{context}

{additional_guidance}

{sa_voice_block}

Generate a reply that:
- Takes the {stance} position but sounds like a person, not a press release
- Brings in constitutional principles naturally (not "Section X states that...")
- References real SA situations to make the point land
- Is respectful but has backbone - you have an opinion
- Can be as long as needed to make a complete argument
- Makes people think, not just agree or disagree
- Avoids lecturing the original poster

DO NOT:
- Sound like a government spokesperson or NGO report
- Use "This highlights the importance of..." or similar AI cliches
- Be preachy or condescending
- Just recite what the Constitution says - connect it to life

DO:
- Sound like someone who lives here and deals with the same stuff
- Use specific examples (not "housing rights" but "eviction notices")
- Ask questions that challenge assumptions
- Show you understand the frustration behind the original tweet

Tone: {tone}

{human_authenticity_check}

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
        params = cls._get_doc_params(doc_context)
        params["sa_voice_block"] = SA_VOICE_BLOCK
        params["opinionated_neutrality_block"] = OPINIONATED_NEUTRALITY_BLOCK
        params["human_authenticity_check"] = HUMAN_AUTHENTICITY_CHECK
        return cls.SYSTEM_PROMPT.format(**params)

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
    def get_external_tweet_reply_prompt(
        cls,
        tweet_text: str,
        author: str,
        stance: str,
        context: str,
        tone: str = "respectful but firm",
        additional_guidance: str = "",
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted external tweet reply prompt.

        Args:
            tweet_text: The text of the external tweet to reply to
            author: The username of the tweet author
            stance: 'agree', 'disagree', or 'neutral'
            context: Relevant document sections
            tone: The tone for the reply
            additional_guidance: Optional additional instructions
            doc_context: Document context for customization
        """
        params = cls._get_doc_params(doc_context)

        # Generate stance-specific guidance
        stance_guidance_map = {
            "agree": "You AGREE with this tweet. Back them up with constitutional principles - but sound like a person agreeing, not a textbook.",
            "disagree": "You DISAGREE with this tweet. Push back using constitutional principles - respectfully but firmly. You're not attacking them, you're disagreeing with the position.",
            "neutral": "Take a NEUTRAL educational stance. Show what the Constitution says about this without picking a side - but don't be boring about it.",
        }
        stance_guidance = stance_guidance_map.get(stance.lower(), stance_guidance_map["neutral"])

        return cls.EXTERNAL_TWEET_REPLY_PROMPT.format(
            tweet_text=tweet_text,
            author=author,
            stance=stance.upper(),
            stance_guidance=stance_guidance,
            context=context,
            tone=tone,
            additional_guidance=additional_guidance,
            sa_voice_block=SA_VOICE_BLOCK,
            human_authenticity_check=HUMAN_AUTHENTICITY_CHECK,
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

{sa_voice_block}

== WRITING STYLE ==
Voice: {persona_description}

Opening style (choose one that fits):
- Start with a specific SA situation (taxi rank, clinic, SASSA office)
- Open with something that happened to "you" or "your friend"
- Lead with a frustration everyone recognizes
- Begin with a question that pokes at something uncomfortable

DO NOT:
- Start with "Did you know" or "It's important to note"
- Use words like "delve", "unpack", "robust", "stakeholder", "empowerment"
- End with "What do you think?" or "Share your thoughts"
- Sound like a government press release or NGO report

DO:
- Sound like someone at a braai sharing something that made them think
- Use contractions naturally
- Reference real SA experiences
- Make it something people would screenshot and share

{human_authenticity_check}

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

{sa_voice_block}

== WRITING STYLE ==
Voice: {persona_description}

Thread flow:
1. Hook: Start with a specific SA scenario that everyone recognizes
2. Build: Show the gap between constitutional promise and daily reality
3. Explain: Bring in the relevant section naturally
4. Challenge: Ask a question that makes people uncomfortable
5. Land: End with something that stays with them (not a lecture)

DO NOT:
- Number tweets as "1/5", "2/5" (let the thread stand alone)
- Use "Let's dive in" or "Let's unpack this"
- Structure as "First... Second... Third..."
- End with generic engagement bait
- Sound like a government press release or NGO report

DO:
- Open with something that happened to real people
- Use transitions that feel like a conversation
- Vary sentence length - short punchy ones, then longer flowing ones
- Reference real SA experiences throughout
- End with a question or observation that sparks debate

{human_authenticity_check}

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
            sa_voice_block=SA_VOICE_BLOCK,
            human_authenticity_check=HUMAN_AUTHENTICITY_CHECK,
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
            sa_voice_block=SA_VOICE_BLOCK,
            human_authenticity_check=HUMAN_AUTHENTICITY_CHECK,
            **params,
        )

    # ========================================================================
    # CONCEPT-BASED SYNTHESIS PROMPTS - For topics without direct document matches
    # ========================================================================

    CONCEPT_SYNTHESIS_TWEET_PROMPT = """Create an educational tweet about how {document_short_name} relates to {topic}.

== CONCEPTUAL FRAMEWORK ==
{concept_context}

== YOUR TASK ==
Think about how this plays out in real South African life:
1. What's the everyday situation where this bites?
2. What's the gap between what the Constitution promises and what happens?
3. What would make someone stop scrolling and engage?

== FORMAT REQUIREMENTS ==
- Maximum 280 characters
- Reference at least one relevant section (e.g., "Section 9", "Section 10")
- Include 1 relevant hashtag
- NO legal advice

{sa_voice_block}

== WRITING STYLE ==
Voice: {persona_description}

DO NOT:
- Ask for more information or say the text wasn't provided
- Start with "It's important to note" or AI cliches
- Be vague or abstract - be specific
- Just define the topic - make a point about it
- Sound like a government press release or NGO report

DO:
- Start with a situation South Africans recognize
- Connect to specific constitutional protections naturally
- Offer a perspective that makes people argue in the replies
- Sound like someone who lives here and deals with this stuff

{human_authenticity_check}

Generate only the tweet text, nothing else."""

    CONCEPT_SYNTHESIS_THREAD_PROMPT = """Create an educational Twitter thread about how {document_short_name} relates to {topic}.

== CONCEPTUAL FRAMEWORK ==
{concept_context}

== YOUR TASK ==
Think about how this plays out in real South African life:
1. What's the everyday situation where ordinary people face this?
2. What does the Constitution say should happen vs what actually happens?
3. What would make this thread get shared and argued about?
4. What uncomfortable truth can you surface?

== FORMAT REQUIREMENTS ==
- Create {num_tweets} connected tweets (280 chars max each)
- Reference relevant sections throughout
- Include hashtags only in the final tweet
- NO legal advice

{sa_voice_block}

== WRITING STYLE ==
Voice: {persona_description}
Thread structure: {thread_structure}

DO NOT:
- Ask for more information or document text
- Start with "Thread:" or "Did you know"
- Use AI cliches like "delve", "unpack", "crucial", "stakeholder"
- Be abstract - use concrete SA examples (taxi rank, clinic, SASSA, etc.)
- Sound like a government press release or NGO report

DO:
- Open with something that happened to someone
- Build a story that shows the gap between promise and reality
- Reference specific SA experiences throughout
- Ask questions that make people uncomfortable
- End with something that sparks debate, not a summary

{human_authenticity_check}

Format your response as:
TWEET 1: [content]
TWEET 2: [content]
...and so on"""

    @classmethod
    def get_concept_tweet_prompt(
        cls,
        topic: str,
        concept_context: str,
        persona_description: str = "conversational and thoughtful",
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted concept-based tweet synthesis prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.CONCEPT_SYNTHESIS_TWEET_PROMPT.format(
            topic=topic,
            concept_context=concept_context,
            persona_description=persona_description,
            sa_voice_block=SA_VOICE_BLOCK,
            human_authenticity_check=HUMAN_AUTHENTICITY_CHECK,
            **params,
        )

    @classmethod
    def get_concept_thread_prompt(
        cls,
        topic: str,
        concept_context: str,
        num_tweets: int = 5,
        thread_structure: str = "progressive revelation",
        persona_description: str = "conversational and thoughtful",
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted concept-based thread synthesis prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.CONCEPT_SYNTHESIS_THREAD_PROMPT.format(
            topic=topic,
            concept_context=concept_context,
            num_tweets=num_tweets,
            thread_structure=thread_structure,
            persona_description=persona_description,
            sa_voice_block=SA_VOICE_BLOCK,
            human_authenticity_check=HUMAN_AUTHENTICITY_CHECK,
            **params,
        )

    CONCEPT_SYNTHESIS_SCRIPT_PROMPT = """Create an educational dialog script about how {document_short_name} relates to {topic}.

== CONCEPTUAL FRAMEWORK ==
{concept_context}

== YOUR TASK ==
Think about how this plays out in real South African conversations:
1. What's a situation that would start this conversation naturally?
2. What do people get wrong about this topic?
3. How does this affect ordinary South Africans in daily life?
4. What would make listeners think "ja, that's exactly it"?

== FORMAT REQUIREMENTS ==
- Write a natural conversation between 2-3 South African characters
- Aim for {duration} of spoken content
- Include specific {section_label_lower} citations naturally in dialog
- End with a clear educational takeaway
- NO legal advice

== CHARACTERS ==
- A person dealing with the situation (the one in the queue, the one who got evicted, etc.)
- A friend or family member who knows a bit about rights (not preachy)
- Optionally, a third voice adding "my cousin had the same thing happen"

{sa_voice_block}

== WRITING STYLE ==
Voice: {persona_description}

DO NOT:
- Ask for more information or document text
- Make characters sound like lawyers or academics
- Use formal language - these are friends talking
- Have characters lecture each other
- Use "stakeholder", "empowerment", "service delivery"

DO:
- Start in the middle of a situation (at the SASSA office, after receiving the eviction notice, etc.)
- Use SA expressions naturally (eish, shame, ja, yoh, hectic)
- Have moments where someone goes "wait, they can't do that?"
- Reference the Constitution as something useful, not abstract
- Include realistic frustrations and emotions
- Include stage directions in [brackets] where helpful

{human_authenticity_check}

Format your response as:
TITLE: [Script title - something catchy, not formal]
CHARACTERS: [List of characters with brief, relatable descriptions]
---
[Character Name]: [Dialog]
[Character Name]: [Dialog]
...
---
TAKEAWAY: [Key lesson - stated simply, not like a textbook]"""

    @classmethod
    def get_concept_script_prompt(
        cls,
        topic: str,
        concept_context: str,
        duration: str = "2-3 minutes",
        persona_description: str = "conversational and engaging",
        doc_context: Optional[DocumentContext] = None,
    ) -> str:
        """Get formatted concept-based script synthesis prompt."""
        params = cls._get_doc_params(doc_context)
        return cls.CONCEPT_SYNTHESIS_SCRIPT_PROMPT.format(
            topic=topic,
            concept_context=concept_context,
            duration=duration,
            persona_description=persona_description,
            sa_voice_block=SA_VOICE_BLOCK,
            human_authenticity_check=HUMAN_AUTHENTICITY_CHECK,
            **params,
        )
