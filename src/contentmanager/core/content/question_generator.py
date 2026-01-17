"""Question generator for interactive content creation.

This module generates clarifying questions to help users create better content
and suggests enhancements for existing generated content.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from contentmanager.core.content.concept_mapper import ConceptMapper


class QuestionCategory(Enum):
    """Categories of questions to ask."""
    AUDIENCE = "audience"
    TONE = "tone"
    ANGLE = "angle"
    EXAMPLE = "example"
    FOCUS = "focus"
    DEPTH = "depth"
    FORMAT = "format"


@dataclass
class ContentQuestion:
    """A question to ask the user about their content."""
    question: str
    category: QuestionCategory
    options: list[str] = field(default_factory=list)
    allows_custom: bool = True
    help_text: Optional[str] = None


@dataclass
class EnhancementSuggestion:
    """A suggestion for enhancing generated content."""
    suggestion: str
    action: str  # What clicking this would do
    category: str  # Type of enhancement
    prompt_modifier: str  # How to modify the prompt


# Pre-generation questions by topic type
AUDIENCE_QUESTIONS = [
    ContentQuestion(
        question="Who is your target audience?",
        category=QuestionCategory.AUDIENCE,
        options=[
            "General public",
            "Students/Youth",
            "Legal professionals",
            "Community leaders",
            "Business owners",
        ],
        help_text="This helps tailor the language and examples used."
    ),
]

TONE_QUESTIONS = [
    ContentQuestion(
        question="What tone should the content have?",
        category=QuestionCategory.TONE,
        options=[
            "Educational & informative",
            "Conversational & friendly",
            "Thought-provoking & challenging",
            "Empowering & action-oriented",
            "Serious & formal",
        ],
        help_text="The tone affects how the message is delivered."
    ),
]

ANGLE_QUESTIONS = [
    ContentQuestion(
        question="What angle or perspective would you like to emphasize?",
        category=QuestionCategory.ANGLE,
        options=[
            "Rights and protections",
            "Responsibilities and duties",
            "Historical context",
            "Current real-world application",
            "Common misconceptions",
            "Practical implications",
        ],
        help_text="This shapes the main focus of the content."
    ),
]

EXAMPLE_QUESTIONS = [
    ContentQuestion(
        question="Should we include a specific type of example?",
        category=QuestionCategory.EXAMPLE,
        options=[
            "Real court case or judgment",
            "Everyday scenario people can relate to",
            "Recent news event",
            "Historical event",
            "Hypothetical situation",
            "No specific example needed",
        ],
        help_text="Examples make abstract rights concrete."
    ),
]

DEPTH_QUESTIONS = [
    ContentQuestion(
        question="How deep should the explanation go?",
        category=QuestionCategory.DEPTH,
        options=[
            "Surface level - just the basics",
            "Moderate - explain key concepts",
            "Deep dive - explore nuances and tensions",
        ],
        help_text="This affects how much detail is included."
    ),
]


# Topic-specific questions
TOPIC_SPECIFIC_QUESTIONS: dict[str, list[ContentQuestion]] = {
    "xenophobia": [
        ContentQuestion(
            question="Which aspect of xenophobia should we focus on?",
            category=QuestionCategory.FOCUS,
            options=[
                "Constitutional protections for all people",
                "The difference between immigration policy and human rights",
                "Community tensions and solutions",
                "Violence and security of person",
                "Economic arguments vs constitutional values",
            ],
        ),
    ],
    "corruption": [
        ContentQuestion(
            question="Which accountability mechanism should we highlight?",
            category=QuestionCategory.FOCUS,
            options=[
                "Chapter 9 institutions (Public Protector, etc.)",
                "Parliamentary oversight",
                "Judicial review by courts",
                "Public participation and transparency",
                "Whistleblower protections",
            ],
        ),
    ],
    "gender equality": [
        ContentQuestion(
            question="Which aspect of gender equality should we explore?",
            category=QuestionCategory.FOCUS,
            options=[
                "Section 9 equality protections",
                "Gender-based violence and Section 12",
                "LGBTQ+ rights under the Constitution",
                "Women in leadership and representation",
                "Cultural practices vs constitutional rights",
            ],
        ),
    ],
    "education": [
        ContentQuestion(
            question="What education issue should we address?",
            category=QuestionCategory.FOCUS,
            options=[
                "Right to basic education (Section 29)",
                "Language in education",
                "Quality vs access",
                "School fees and affordability",
                "Children's rights in education",
            ],
        ),
    ],
    "housing": [
        ContentQuestion(
            question="Which housing aspect is most relevant?",
            category=QuestionCategory.FOCUS,
            options=[
                "Right to adequate housing (Section 26)",
                "Protection against eviction",
                "Progressive realization",
                "Informal settlements",
                "State's housing obligations",
            ],
        ),
    ],
}


# Enhancement suggestions for different content types
TWEET_ENHANCEMENTS = [
    EnhancementSuggestion(
        suggestion="Add a thought-provoking question",
        action="enhance_with_question",
        category="engagement",
        prompt_modifier="Add a rhetorical question that makes readers think deeper about this issue.",
    ),
    EnhancementSuggestion(
        suggestion="Include a relatable scenario",
        action="add_scenario",
        category="relatability",
        prompt_modifier="Add a brief, relatable everyday scenario that illustrates this point.",
    ),
    EnhancementSuggestion(
        suggestion="Make it more provocative/challenging",
        action="increase_provocation",
        category="tone",
        prompt_modifier="Make the content more thought-provoking and challenging to common assumptions.",
    ),
    EnhancementSuggestion(
        suggestion="Simplify the language",
        action="simplify",
        category="accessibility",
        prompt_modifier="Simplify the language to be more accessible to a general audience.",
    ),
    EnhancementSuggestion(
        suggestion="Add urgency or call to awareness",
        action="add_urgency",
        category="engagement",
        prompt_modifier="Add a sense of urgency or importance to raise awareness about this issue.",
    ),
]

THREAD_ENHANCEMENTS = [
    EnhancementSuggestion(
        suggestion="Add a real-world example",
        action="add_example",
        category="relatability",
        prompt_modifier="Include a specific real-world example or case study.",
    ),
    EnhancementSuggestion(
        suggestion="Address a common misconception",
        action="add_misconception",
        category="education",
        prompt_modifier="Add a tweet addressing a common misconception about this topic.",
    ),
    EnhancementSuggestion(
        suggestion="Include opposing viewpoints",
        action="add_nuance",
        category="balance",
        prompt_modifier="Acknowledge different perspectives or tensions around this issue.",
    ),
    EnhancementSuggestion(
        suggestion="Make the hook stronger",
        action="improve_hook",
        category="engagement",
        prompt_modifier="Rewrite the opening tweet to be more attention-grabbing.",
    ),
    EnhancementSuggestion(
        suggestion="Add practical takeaways",
        action="add_practical",
        category="actionable",
        prompt_modifier="Add practical takeaways - what can people actually do with this knowledge?",
    ),
]

SCRIPT_ENHANCEMENTS = [
    EnhancementSuggestion(
        suggestion="Add more character conflict/tension",
        action="add_conflict",
        category="engagement",
        prompt_modifier="Add more disagreement or tension between characters to make it more engaging.",
    ),
    EnhancementSuggestion(
        suggestion="Include an 'aha moment'",
        action="add_aha",
        category="education",
        prompt_modifier="Include a clear moment where a character has a realization or insight.",
    ),
    EnhancementSuggestion(
        suggestion="Make dialogue more natural",
        action="naturalize",
        category="authenticity",
        prompt_modifier="Make the dialogue sound more natural and less like a textbook.",
    ),
    EnhancementSuggestion(
        suggestion="Add humor or lighter moments",
        action="add_humor",
        category="tone",
        prompt_modifier="Add appropriate humor or lighter moments to balance the educational content.",
    ),
    EnhancementSuggestion(
        suggestion="Strengthen the takeaway",
        action="improve_takeaway",
        category="impact",
        prompt_modifier="Make the final takeaway more memorable and impactful.",
    ),
]


class QuestionGenerator:
    """Generates questions and enhancement suggestions for content creation."""

    def __init__(self):
        self.concept_mapper = ConceptMapper()

    def get_pre_generation_questions(
        self,
        topic: str,
        content_type: str = "tweet",
        max_questions: int = 4,
    ) -> list[ContentQuestion]:
        """Get questions to ask before generating content.

        Args:
            topic: The topic for content generation.
            content_type: Type of content (tweet, thread, script).
            max_questions: Maximum number of questions to return.

        Returns:
            List of questions to ask the user.
        """
        questions = []

        # Always include audience and tone
        questions.extend(AUDIENCE_QUESTIONS)
        questions.extend(TONE_QUESTIONS)

        # Add angle question for threads and scripts
        if content_type in ("thread", "script"):
            questions.extend(ANGLE_QUESTIONS)

        # Add topic-specific questions if available
        topic_lower = topic.lower().strip()
        for key, topic_questions in TOPIC_SPECIFIC_QUESTIONS.items():
            if key in topic_lower or topic_lower in key:
                questions.extend(topic_questions)
                break

        # Check concept mapper for related topics
        mapping = self.concept_mapper.map_topic(topic)
        if mapping and topic_lower not in TOPIC_SPECIFIC_QUESTIONS:
            # Generate a focus question based on perspective angles
            if mapping.perspective_angles:
                focus_question = ContentQuestion(
                    question=f"Which perspective on {topic} would you like to emphasize?",
                    category=QuestionCategory.FOCUS,
                    options=mapping.perspective_angles[:5],  # Max 5 options
                )
                questions.append(focus_question)

        # Add example question for longer content
        if content_type in ("thread", "script"):
            questions.extend(EXAMPLE_QUESTIONS)

        # Add depth question for scripts
        if content_type == "script":
            questions.extend(DEPTH_QUESTIONS)

        return questions[:max_questions]

    def get_enhancement_suggestions(
        self,
        content: str,
        content_type: str,
        topic: str,
        max_suggestions: int = 4,
    ) -> list[EnhancementSuggestion]:
        """Get suggestions for enhancing generated content.

        Args:
            content: The generated content.
            content_type: Type of content (tweet, thread, script).
            topic: The topic of the content.
            max_suggestions: Maximum number of suggestions to return.

        Returns:
            List of enhancement suggestions.
        """
        if content_type == "tweet":
            base_suggestions = TWEET_ENHANCEMENTS.copy()
        elif content_type == "thread":
            base_suggestions = THREAD_ENHANCEMENTS.copy()
        elif content_type == "script":
            base_suggestions = SCRIPT_ENHANCEMENTS.copy()
        else:
            base_suggestions = TWEET_ENHANCEMENTS.copy()

        # Analyze content to prioritize relevant suggestions
        suggestions = self._prioritize_suggestions(content, base_suggestions)

        return suggestions[:max_suggestions]

    def _prioritize_suggestions(
        self,
        content: str,
        suggestions: list[EnhancementSuggestion],
    ) -> list[EnhancementSuggestion]:
        """Prioritize suggestions based on content analysis.

        Args:
            content: The content to analyze.
            suggestions: Available suggestions.

        Returns:
            Prioritized list of suggestions.
        """
        content_lower = content.lower()
        prioritized = []
        regular = []

        for suggestion in suggestions:
            # Check if this type of enhancement is already present
            should_deprioritize = False

            if suggestion.action == "add_scenario" and any(
                word in content_lower for word in ["imagine", "picture", "scenario", "example"]
            ):
                should_deprioritize = True

            if suggestion.action == "enhance_with_question" and "?" in content:
                should_deprioritize = True

            if should_deprioritize:
                regular.append(suggestion)
            else:
                prioritized.append(suggestion)

        return prioritized + regular

    def build_enhanced_prompt(
        self,
        base_topic: str,
        answers: dict[str, str],
        content_type: str = "tweet",
    ) -> dict:
        """Build enhanced generation parameters from user answers.

        Args:
            base_topic: The original topic.
            answers: User's answers to questions (category -> answer).
            content_type: Type of content to generate.

        Returns:
            Dict with enhanced prompt parameters.
        """
        enhancements = []
        persona_hints = []

        # Process audience answer
        audience = answers.get("audience", "").lower()
        if "student" in audience or "youth" in audience:
            enhancements.append("Use relatable examples for young people")
            persona_hints.append("youthful and engaging")
        elif "legal" in audience:
            enhancements.append("Include precise legal references")
            persona_hints.append("professionally informed")
        elif "community" in audience:
            enhancements.append("Focus on practical community applications")
            persona_hints.append("community-minded")
        elif "business" in audience:
            enhancements.append("Include business/economic implications")
            persona_hints.append("practically oriented")

        # Process tone answer
        tone = answers.get("tone", "").lower()
        if "conversational" in tone or "friendly" in tone:
            persona_hints.append("warm and approachable")
        elif "thought-provoking" in tone or "challenging" in tone:
            persona_hints.append("intellectually provocative")
            enhancements.append("Challenge common assumptions")
        elif "empowering" in tone or "action" in tone:
            persona_hints.append("inspiring and empowering")
            enhancements.append("Include a call to awareness or action")
        elif "serious" in tone or "formal" in tone:
            persona_hints.append("serious and authoritative")

        # Process angle answer
        angle = answers.get("angle", "")
        if angle:
            enhancements.append(f"Emphasize: {angle}")

        # Process focus answer
        focus = answers.get("focus", "")
        if focus:
            enhancements.append(f"Focus on: {focus}")

        # Process example answer
        example = answers.get("example", "").lower()
        if "court case" in example or "judgment" in example:
            enhancements.append("Include reference to a relevant court case")
        elif "everyday" in example or "relatable" in example:
            enhancements.append("Include a relatable everyday scenario")
        elif "news" in example:
            enhancements.append("Reference recent news or current events")
        elif "historical" in example:
            enhancements.append("Include historical context or example")

        # Process depth answer
        depth = answers.get("depth", "").lower()
        if "deep" in depth or "nuance" in depth:
            enhancements.append("Explore nuances and tensions in detail")
        elif "surface" in depth or "basic" in depth:
            enhancements.append("Keep explanation simple and accessible")

        # Process enhancement modifier (from post-generation enhancement suggestions)
        enhancement_modifier = answers.get("enhancement", "")
        if enhancement_modifier:
            enhancements.append(enhancement_modifier)

        # Build the enhanced parameters
        enhancement_text = "\n".join(f"- {e}" for e in enhancements) if enhancements else ""
        persona_text = ", ".join(persona_hints) if persona_hints else "conversational"

        return {
            "topic": base_topic,
            "enhancement_instructions": enhancement_text,
            "persona_description": persona_text,
            "content_type": content_type,
        }

    def get_refinement_questions(
        self,
        content: str,
        content_type: str,
    ) -> list[ContentQuestion]:
        """Get questions to help refine existing content.

        Args:
            content: The existing content.
            content_type: Type of content.

        Returns:
            List of refinement questions.
        """
        questions = []

        questions.append(ContentQuestion(
            question="What aspect would you like to improve?",
            category=QuestionCategory.FOCUS,
            options=[
                "Make it more engaging/attention-grabbing",
                "Add more concrete examples",
                "Simplify the language",
                "Make it more thought-provoking",
                "Add more section citations",
                "Change the tone",
            ],
        ))

        if content_type == "thread":
            questions.append(ContentQuestion(
                question="Which part of the thread needs work?",
                category=QuestionCategory.FOCUS,
                options=[
                    "The opening hook",
                    "The middle explanation",
                    "The conclusion/takeaway",
                    "The overall flow",
                ],
            ))

        if content_type == "script":
            questions.append(ContentQuestion(
                question="What would make the script better?",
                category=QuestionCategory.FOCUS,
                options=[
                    "More natural dialogue",
                    "Stronger character voices",
                    "Better educational content",
                    "More engaging conflict/tension",
                    "Clearer takeaway message",
                ],
            ))

        return questions
