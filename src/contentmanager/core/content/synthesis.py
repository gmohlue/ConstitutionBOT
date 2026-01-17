"""Synthesis Engine Module.

This module transforms insights into original, synthesized content
using various synthesis modes and strategies.
"""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from contentmanager.core.content.insight_analyzer import SectionInsight


class SynthesisMode(Enum):
    """Modes for content synthesis."""

    EXPLAIN = "explain"  # Break down complex ideas simply
    CONTRAST = "contrast"  # Compare with everyday intuitions
    CHALLENGE = "challenge"  # Present provocative angles
    APPLY = "apply"  # Show real-world applications
    STORY = "story"  # Tell through narrative
    MYTH_BUST = "myth_bust"  # Debunk common misconceptions
    IMPLICATIONS = "implications"  # Explore what it really means


@dataclass
class SynthesisContext:
    """Context for content synthesis."""

    insights: list[SectionInsight]
    mode: SynthesisMode
    target_audience: str = "general"
    scenario_category: Optional[str] = None
    persona_description: Optional[str] = None
    max_length: Optional[int] = None

    def get_primary_insight(self) -> Optional[SectionInsight]:
        """Get the primary insight for synthesis."""
        if self.insights:
            # Return the highest quality insight
            return max(self.insights, key=lambda i: i.insight_quality_score)
        return None


@dataclass
class SynthesizedContent:
    """Result of content synthesis."""

    raw_text: str
    mode: SynthesisMode
    hook: str = ""
    main_body: str = ""
    closing: str = ""
    source_sections: list[int] = field(default_factory=list)

    # Metadata
    synthesis_score: float = 0.0  # Quality score
    perspective_angle: str = ""  # What angle was taken

    @property
    def full_content(self) -> str:
        """Get full synthesized content."""
        if self.hook and self.main_body:
            parts = [self.hook, self.main_body]
            if self.closing:
                parts.append(self.closing)
            return " ".join(parts)
        return self.raw_text


@dataclass
class NarrativeFrame:
    """A narrative structure for story-based synthesis."""

    setup: str  # The situation or context
    tension: str  # The conflict or question
    insight: str  # The key realization
    resolution: str  # How it resolves or what it means

    def to_narrative(self) -> str:
        """Convert frame to narrative text."""
        return f"{self.setup} {self.tension} {self.insight} {self.resolution}"


class SynthesisEngine:
    """Transforms insights into original synthesized content."""

    # Hook templates by mode
    HOOK_TEMPLATES = {
        SynthesisMode.EXPLAIN: [
            "Here's what {topic} actually means in plain terms:",
            "Breaking down {topic} - no jargon:",
            "The simplest way to understand {topic}:",
            "{topic} sounds complicated. It's not.",
        ],
        SynthesisMode.CONTRAST: [
            "You'd think {topic} works one way. It doesn't.",
            "Common sense says X. {topic} says otherwise.",
            "What most people assume about {topic} vs reality:",
            "The gap between intuition and {topic}:",
        ],
        SynthesisMode.CHALLENGE: [
            "Unpopular take on {topic}:",
            "What if we're thinking about {topic} all wrong?",
            "The uncomfortable truth about {topic}:",
            "Here's the {topic} conversation nobody wants to have:",
        ],
        SynthesisMode.APPLY: [
            "How {topic} shows up in your daily life:",
            "That moment when {topic} actually matters:",
            "Real scenario: {topic} in action:",
            "When {topic} stops being abstract:",
        ],
        SynthesisMode.STORY: [
            "Picture this:",
            "There's this moment when",
            "It starts like this:",
            "Small scene, big meaning:",
        ],
        SynthesisMode.MYTH_BUST: [
            "Myth: {misconception}. Reality:",
            "Stop believing this about {topic}:",
            "That thing everyone gets wrong about {topic}:",
            "Let's kill a myth about {topic}:",
        ],
        SynthesisMode.IMPLICATIONS: [
            "What {topic} really means for you:",
            "The ripple effects of {topic} nobody talks about:",
            "Follow the thread: {topic} leads to...",
            "Beyond the text: what {topic} actually changes:",
        ],
    }

    # Perspective angles for challenging content
    CHALLENGE_ANGLES = [
        "The limitation nobody mentions",
        "What this right actually costs",
        "Why this is harder than it sounds",
        "The trade-off hidden in plain sight",
        "Who this doesn't protect (and why)",
        "The enforcement gap",
        "Paper rights vs real rights",
    ]

    # Story structures
    STORY_STRUCTURES = [
        "problem_discovery_solution",
        "before_event_after",
        "ordinary_disruption_new_normal",
        "question_exploration_insight",
    ]

    def __init__(self, llm_provider: Optional[object] = None):
        """Initialize the synthesis engine.

        Args:
            llm_provider: Optional LLM provider for enhanced synthesis.
        """
        self._llm = llm_provider

    async def synthesize(
        self,
        context: SynthesisContext
    ) -> SynthesizedContent:
        """Synthesize content from insights using specified mode.

        Args:
            context: The synthesis context with insights and parameters.

        Returns:
            SynthesizedContent with the generated content.
        """
        primary = context.get_primary_insight()
        if not primary:
            return SynthesizedContent(
                raw_text="Insufficient insights for synthesis",
                mode=context.mode
            )

        # Generate based on mode
        if context.mode == SynthesisMode.EXPLAIN:
            return await self._synthesize_explanation(context, primary)
        elif context.mode == SynthesisMode.CONTRAST:
            return await self._synthesize_contrast(context, primary)
        elif context.mode == SynthesisMode.CHALLENGE:
            return await self._synthesize_challenge(context, primary)
        elif context.mode == SynthesisMode.APPLY:
            return await self._synthesize_application(context, primary)
        elif context.mode == SynthesisMode.STORY:
            return await self._synthesize_story(context, primary)
        elif context.mode == SynthesisMode.MYTH_BUST:
            return await self._synthesize_myth_bust(context, primary)
        elif context.mode == SynthesisMode.IMPLICATIONS:
            return await self._synthesize_implications(context, primary)
        else:
            return await self._synthesize_explanation(context, primary)

    def synthesize_perspective(
        self,
        insight: SectionInsight,
        mode: SynthesisMode,
        scenario: Optional[str] = None
    ) -> str:
        """Transform insight into original perspective content.

        Args:
            insight: The section insight to transform.
            mode: The synthesis mode to use.
            scenario: Optional scenario context.

        Returns:
            Synthesized perspective text.
        """
        # Build perspective based on mode
        if mode == SynthesisMode.CHALLENGE:
            angle = random.choice(self.CHALLENGE_ANGLES)
            return self._build_challenge_perspective(insight, angle)
        elif mode == SynthesisMode.CONTRAST:
            return self._build_contrast_perspective(insight)
        elif mode == SynthesisMode.APPLY:
            return self._build_application_perspective(insight, scenario)
        else:
            return self._build_basic_perspective(insight)

    def generate_hook(
        self,
        insight: SectionInsight,
        mode: SynthesisMode
    ) -> str:
        """Generate an attention-grabbing opener.

        Args:
            insight: The insight to hook from.
            mode: The synthesis mode.

        Returns:
            Hook text.
        """
        templates = self.HOOK_TEMPLATES.get(mode, self.HOOK_TEMPLATES[SynthesisMode.EXPLAIN])
        template = random.choice(templates)

        # Replace placeholders
        topic = insight.section_title or f"Section {insight.section_number}"

        if "{misconception}" in template and insight.common_misconceptions:
            misconception = random.choice(insight.common_misconceptions)
            return template.format(topic=topic, misconception=misconception)

        return template.format(topic=topic)

    def create_narrative_frame(
        self,
        insight: SectionInsight,
        structure: Optional[str] = None
    ) -> NarrativeFrame:
        """Build a story structure for narrative synthesis.

        Args:
            insight: The insight to frame.
            structure: Optional specific structure to use.

        Returns:
            NarrativeFrame with story elements.
        """
        structure = structure or random.choice(self.STORY_STRUCTURES)

        if structure == "problem_discovery_solution":
            return self._frame_problem_discovery(insight)
        elif structure == "before_event_after":
            return self._frame_before_after(insight)
        elif structure == "ordinary_disruption_new_normal":
            return self._frame_disruption(insight)
        else:  # question_exploration_insight
            return self._frame_exploration(insight)

    def build_argument(
        self,
        insight: SectionInsight,
        thesis: Optional[str] = None
    ) -> dict:
        """Construct a thesis + evidence argument structure.

        Args:
            insight: The insight to build argument from.
            thesis: Optional specific thesis statement.

        Returns:
            Dict with 'thesis', 'evidence', and 'conclusion'.
        """
        if not thesis:
            thesis = self._generate_thesis(insight)

        evidence = self._gather_evidence(insight)
        conclusion = self._draw_conclusion(insight, thesis)

        return {
            "thesis": thesis,
            "evidence": evidence,
            "conclusion": conclusion
        }

    # Private synthesis methods

    async def _synthesize_explanation(
        self,
        context: SynthesisContext,
        primary: SectionInsight
    ) -> SynthesizedContent:
        """Synthesize explanatory content."""
        hook = self.generate_hook(primary, SynthesisMode.EXPLAIN)

        # Build main body from insight components
        main_parts = []

        if primary.core_principle:
            main_parts.append(f"At its core: {primary.core_principle}.")

        if primary.practical_meaning:
            main_parts.append(f"In practice, this means {primary.practical_meaning.lower()}.")

        if primary.analogies:
            analogy = random.choice(primary.analogies)
            main_parts.append(f"Think of it {analogy.lower()}.")

        main_body = " ".join(main_parts)

        # Closing with implication
        closing = ""
        if primary.implications:
            closing = random.choice(primary.implications)

        return SynthesizedContent(
            raw_text=f"{hook} {main_body} {closing}".strip(),
            mode=SynthesisMode.EXPLAIN,
            hook=hook,
            main_body=main_body,
            closing=closing,
            source_sections=[primary.section_number],
            synthesis_score=self._calculate_synthesis_score(hook, main_body, closing),
            perspective_angle="explanation"
        )

    async def _synthesize_contrast(
        self,
        context: SynthesisContext,
        primary: SectionInsight
    ) -> SynthesizedContent:
        """Synthesize content that contrasts intuition with reality."""
        hook = self.generate_hook(primary, SynthesisMode.CONTRAST)

        # Build contrast between expectation and reality
        main_parts = []

        # What people expect
        expectation = self._generate_common_expectation(primary)
        main_parts.append(f"Most people assume {expectation}.")

        # What's actually true
        if primary.core_principle:
            main_parts.append(f"But the actual principle: {primary.core_principle}.")

        # The key difference
        if primary.common_misconceptions:
            misconception = random.choice(primary.common_misconceptions)
            main_parts.append(f"Key difference: {misconception}")

        main_body = " ".join(main_parts)
        closing = "The gap matters more than you'd think."

        return SynthesizedContent(
            raw_text=f"{hook} {main_body} {closing}".strip(),
            mode=SynthesisMode.CONTRAST,
            hook=hook,
            main_body=main_body,
            closing=closing,
            source_sections=[primary.section_number],
            synthesis_score=self._calculate_synthesis_score(hook, main_body, closing),
            perspective_angle="contrast"
        )

    async def _synthesize_challenge(
        self,
        context: SynthesisContext,
        primary: SectionInsight
    ) -> SynthesizedContent:
        """Synthesize provocative, challenging content."""
        hook = self.generate_hook(primary, SynthesisMode.CHALLENGE)
        angle = random.choice(self.CHALLENGE_ANGLES)

        main_parts = []

        # Present the challenge
        if primary.tensions:
            tension = random.choice(primary.tensions)
            main_parts.append(f"Here's the tension: {tension}")

        # The uncomfortable truth
        if primary.edge_cases:
            edge = random.choice(primary.edge_cases)
            main_parts.append(f"Edge case to consider: {edge}")
        else:
            main_parts.append(f"The angle nobody discusses: {angle.lower()}.")

        # Why it matters
        if primary.implications:
            implication = random.choice(primary.implications)
            main_parts.append(implication)

        main_body = " ".join(main_parts)
        closing = "Worth sitting with that for a moment."

        return SynthesizedContent(
            raw_text=f"{hook} {main_body} {closing}".strip(),
            mode=SynthesisMode.CHALLENGE,
            hook=hook,
            main_body=main_body,
            closing=closing,
            source_sections=[primary.section_number],
            synthesis_score=self._calculate_synthesis_score(hook, main_body, closing),
            perspective_angle=angle
        )

    async def _synthesize_application(
        self,
        context: SynthesisContext,
        primary: SectionInsight
    ) -> SynthesizedContent:
        """Synthesize content showing real-world application."""
        hook = self.generate_hook(primary, SynthesisMode.APPLY)

        main_parts = []

        # The practical scenario
        scenario = context.scenario_category or "daily life"
        if primary.practical_meaning:
            main_parts.append(f"In {scenario}: {primary.practical_meaning}")

        # Concrete example
        if primary.analogies:
            analogy = random.choice(primary.analogies)
            main_parts.append(f"Real example: {analogy}")

        # What to actually do
        main_parts.append(
            "When this comes up, know that this provision has your back."
        )

        main_body = " ".join(main_parts)
        closing = ""

        return SynthesizedContent(
            raw_text=f"{hook} {main_body}".strip(),
            mode=SynthesisMode.APPLY,
            hook=hook,
            main_body=main_body,
            closing=closing,
            source_sections=[primary.section_number],
            synthesis_score=self._calculate_synthesis_score(hook, main_body, closing),
            perspective_angle="application"
        )

    async def _synthesize_story(
        self,
        context: SynthesisContext,
        primary: SectionInsight
    ) -> SynthesizedContent:
        """Synthesize narrative content."""
        frame = self.create_narrative_frame(primary)
        hook = frame.setup
        main_body = f"{frame.tension} {frame.insight}"
        closing = frame.resolution

        return SynthesizedContent(
            raw_text=frame.to_narrative(),
            mode=SynthesisMode.STORY,
            hook=hook,
            main_body=main_body,
            closing=closing,
            source_sections=[primary.section_number],
            synthesis_score=self._calculate_synthesis_score(hook, main_body, closing),
            perspective_angle="narrative"
        )

    async def _synthesize_myth_bust(
        self,
        context: SynthesisContext,
        primary: SectionInsight
    ) -> SynthesizedContent:
        """Synthesize myth-busting content."""
        hook = self.generate_hook(primary, SynthesisMode.MYTH_BUST)

        main_parts = []

        # The myth
        if primary.common_misconceptions:
            myth = random.choice(primary.common_misconceptions)
            main_parts.append(f"The myth: {myth}")
        else:
            main_parts.append("The common assumption is wrong.")

        # The reality
        if primary.core_principle:
            main_parts.append(f"The reality: {primary.core_principle}")

        # Why it matters
        main_parts.append("Understanding the difference changes how you approach this.")

        main_body = " ".join(main_parts)
        closing = ""

        return SynthesizedContent(
            raw_text=f"{hook} {main_body}".strip(),
            mode=SynthesisMode.MYTH_BUST,
            hook=hook,
            main_body=main_body,
            closing=closing,
            source_sections=[primary.section_number],
            synthesis_score=self._calculate_synthesis_score(hook, main_body, closing),
            perspective_angle="myth_bust"
        )

    async def _synthesize_implications(
        self,
        context: SynthesisContext,
        primary: SectionInsight
    ) -> SynthesizedContent:
        """Synthesize implications-focused content."""
        hook = self.generate_hook(primary, SynthesisMode.IMPLICATIONS)

        main_parts = []

        # Chain of implications
        if primary.implications:
            for imp in primary.implications[:2]:
                main_parts.append(imp)
        else:
            main_parts.append(
                "This provision creates ripple effects most people don't notice."
            )

        # Hidden connection
        if primary.related_concepts:
            concept = random.choice(primary.related_concepts)
            main_parts.append(f"Connected to: {concept}")

        main_body = " ".join(main_parts)
        closing = "Follow the thread far enough and the pattern becomes clear."

        return SynthesizedContent(
            raw_text=f"{hook} {main_body} {closing}".strip(),
            mode=SynthesisMode.IMPLICATIONS,
            hook=hook,
            main_body=main_body,
            closing=closing,
            source_sections=[primary.section_number],
            synthesis_score=self._calculate_synthesis_score(hook, main_body, closing),
            perspective_angle="implications"
        )

    # Narrative frame builders

    def _frame_problem_discovery(self, insight: SectionInsight) -> NarrativeFrame:
        """Create problem-discovery-solution frame."""
        return NarrativeFrame(
            setup=f"Someone runs into a problem with {insight.section_title.lower()}.",
            tension=f"They don't realize {insight.practical_meaning.lower() if insight.practical_meaning else 'what their rights actually are'}.",
            insight=f"Then they discover: {insight.core_principle or 'the provision that protects them'}.",
            resolution="Suddenly the situation looks different."
        )

    def _frame_before_after(self, insight: SectionInsight) -> NarrativeFrame:
        """Create before-event-after frame."""
        return NarrativeFrame(
            setup="Before understanding this provision, things seemed one way.",
            tension=f"Then came the realization about {insight.section_title.lower()}.",
            insight=insight.core_principle or "The principle changes the calculation.",
            resolution="After: a clearer picture of what's actually at stake."
        )

    def _frame_disruption(self, insight: SectionInsight) -> NarrativeFrame:
        """Create ordinary-disruption-new normal frame."""
        return NarrativeFrame(
            setup="Ordinary day. Nothing special happening.",
            tension=f"Until {insight.section_title.lower()} suddenly becomes relevant.",
            insight=insight.practical_meaning or "This is when the provision matters.",
            resolution="New normal: knowing this right exists and when to invoke it."
        )

    def _frame_exploration(self, insight: SectionInsight) -> NarrativeFrame:
        """Create question-exploration-insight frame."""
        return NarrativeFrame(
            setup=f"Question: What does {insight.section_title.lower()} actually mean?",
            tension="Dig past the surface language.",
            insight=insight.core_principle or "The deeper principle emerges.",
            resolution=insight.practical_meaning or "Now it makes practical sense."
        )

    # Helper methods

    def _build_challenge_perspective(
        self,
        insight: SectionInsight,
        angle: str
    ) -> str:
        """Build challenging perspective content."""
        parts = [f"Looking at {insight.section_title} through the lens of '{angle}':"]

        if insight.tensions:
            parts.append(random.choice(insight.tensions))

        if insight.implications:
            parts.append(random.choice(insight.implications))

        return " ".join(parts)

    def _build_contrast_perspective(self, insight: SectionInsight) -> str:
        """Build contrast perspective content."""
        expectation = self._generate_common_expectation(insight)
        parts = [
            f"Expectation: {expectation}",
            f"Reality: {insight.core_principle or insight.practical_meaning or 'Different.'}"
        ]
        return " ".join(parts)

    def _build_application_perspective(
        self,
        insight: SectionInsight,
        scenario: Optional[str]
    ) -> str:
        """Build application perspective content."""
        context = scenario or "everyday situations"
        parts = [f"In {context}, {insight.section_title.lower()} means:"]

        if insight.practical_meaning:
            parts.append(insight.practical_meaning)

        return " ".join(parts)

    def _build_basic_perspective(self, insight: SectionInsight) -> str:
        """Build basic perspective content."""
        return insight.core_principle or insight.practical_meaning or insight.section_title

    def _generate_common_expectation(self, insight: SectionInsight) -> str:
        """Generate what people commonly expect about an insight."""
        text_lower = insight.section_text.lower()

        if "right" in text_lower:
            return "rights are absolute and unlimited"
        elif "freedom" in text_lower:
            return "freedom means no restrictions at all"
        elif "equality" in text_lower:
            return "equality means treating everyone identically"
        elif "property" in text_lower:
            return "property rights are unconditional"
        else:
            return "this provision is straightforward"

    def _generate_thesis(self, insight: SectionInsight) -> str:
        """Generate a thesis statement from insight."""
        if insight.core_principle:
            return f"The core of {insight.section_title}: {insight.core_principle}"
        return f"{insight.section_title} matters more than commonly understood"

    def _gather_evidence(self, insight: SectionInsight) -> list[str]:
        """Gather evidence points from insight."""
        evidence = []

        if insight.practical_meaning:
            evidence.append(f"Practical impact: {insight.practical_meaning}")

        if insight.implications:
            evidence.extend(insight.implications[:2])

        if insight.analogies:
            evidence.append(f"Comparison: {insight.analogies[0]}")

        return evidence

    def _draw_conclusion(self, insight: SectionInsight, thesis: str) -> str:
        """Draw a conclusion from thesis and insight."""
        if insight.tensions:
            return f"The balance to maintain: {insight.tensions[0]}"
        return "Understanding this provision equips you to navigate real situations."

    def _calculate_synthesis_score(
        self,
        hook: str,
        main_body: str,
        closing: str
    ) -> float:
        """Calculate quality score for synthesized content."""
        score = 0.0

        # Has hook
        if hook:
            score += 0.3

        # Has substantial main body
        if main_body and len(main_body) > 50:
            score += 0.4

        # Has closing
        if closing:
            score += 0.2

        # Variety in sentence length
        all_text = f"{hook} {main_body} {closing}"
        sentences = [s.strip() for s in all_text.split('.') if s.strip()]
        if len(sentences) > 1:
            lengths = [len(s.split()) for s in sentences]
            variance = max(lengths) - min(lengths)
            if variance > 5:
                score += 0.1

        return min(score, 1.0)
