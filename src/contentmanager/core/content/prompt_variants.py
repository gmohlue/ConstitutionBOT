"""Prompt Variants Module.

This module provides randomized prompt variations to prevent repetitive
content patterns and maintain fresh, engaging output.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OpeningStyle(Enum):
    """Styles for content openings."""

    SURPRISING_FACT = "surprising_fact"
    QUESTION = "question"
    SCENARIO = "scenario"
    MISCONCEPTION = "misconception"
    PROVOCATIVE = "provocative"
    OBSERVATION = "observation"
    CONTRAST = "contrast"


class ThreadStructure(Enum):
    """Structural patterns for threads."""

    PROBLEM_SOLUTION = "problem_solution"
    MYTH_REALITY = "myth_reality"
    STORY_ARC = "story_arc"
    COUNTDOWN = "countdown"
    LAYERS = "layers"
    JOURNEY = "journey"
    COMPARISON = "comparison"


@dataclass
class PromptVariant:
    """A prompt variant configuration."""

    name: str
    opening_template: str
    structure_hint: str
    tone_guidance: str
    closing_style: str


class PromptVariants:
    """Provides randomized prompt variations to prevent repetition."""

    # Tweet opening variants
    TWEET_OPENINGS = {
        OpeningStyle.SURPRISING_FACT: [
            "Most people don't realize: {insight}",
            "Here's what surprised me about {topic}: {insight}",
            "The part nobody talks about: {insight}",
            "Little-known fact about {topic}: {insight}",
            "Plot twist about {topic}: {insight}",
        ],
        OpeningStyle.QUESTION: [
            "Ever wondered why {topic} works this way?",
            "What happens when {scenario}?",
            "Why does {topic} matter more than you think?",
            "When was the last time you thought about {topic}?",
            "What if I told you {insight}?",
        ],
        OpeningStyle.SCENARIO: [
            "You're in {scenario}. Here's what protects you:",
            "Picture this: {scenario}",
            "Imagine: {scenario}",
            "Real situation: {scenario}",
            "It happens more than you'd think: {scenario}",
        ],
        OpeningStyle.MISCONCEPTION: [
            "Common myth about {topic}: {misconception}. Reality:",
            "What people get wrong about {topic}:",
            "Everyone assumes {misconception}. Here's the truth:",
            "Stop believing this about {topic}:",
            "The {topic} misconception that won't die:",
        ],
        OpeningStyle.PROVOCATIVE: [
            "Hot take on {topic}:",
            "Unpopular opinion: {topic} isn't what you think",
            "Let's be uncomfortable about {topic} for a second:",
            "The {topic} conversation no one wants to have:",
            "Brace yourself: {insight}",
        ],
        OpeningStyle.OBSERVATION: [
            "Something I've noticed about {topic}:",
            "Been thinking about {topic} lately. Here's what stands out:",
            "Small observation with big implications about {topic}:",
            "Quiet truth about {topic}:",
            "The thing about {topic} that keeps coming up:",
        ],
        OpeningStyle.CONTRAST: [
            "On paper: {expectation}. In reality: {reality}",
            "What we say about {topic} vs what actually happens:",
            "The gap between the ideal and reality of {topic}:",
            "{topic} in theory vs {topic} in practice:",
            "Expectation: {expectation}. Reality: {reality}",
        ],
    }

    # Thread structure templates
    THREAD_STRUCTURES = {
        ThreadStructure.PROBLEM_SOLUTION: {
            "intro": "There's a problem with how we think about {topic}. Thread 🧵",
            "structure": [
                "THE PROBLEM: {problem_statement}",
                "WHY IT MATTERS: {impact}",
                "WHAT MOST PEOPLE MISS: {hidden_aspect}",
                "THE SOLUTION: {solution}",
                "KEY TAKEAWAY: {takeaway}",
            ],
            "tone": "Analytical and constructive",
        },
        ThreadStructure.MYTH_REALITY: {
            "intro": "5 myths about {topic} that need to die. Thread 🧵",
            "structure": [
                "MYTH 1: {myth}. REALITY: {reality}",
                "MYTH 2: {myth}. REALITY: {reality}",
                "MYTH 3: {myth}. REALITY: {reality}",
                "MYTH 4: {myth}. REALITY: {reality}",
                "MYTH 5: {myth}. REALITY: {reality}",
                "WHY THESE MYTHS PERSIST: {explanation}",
            ],
            "tone": "Corrective but not condescending",
        },
        ThreadStructure.STORY_ARC: {
            "intro": "Let me tell you about {topic}. A thread 🧵",
            "structure": [
                "THE BEGINNING: {setup}",
                "THE TENSION: {conflict}",
                "THE TURNING POINT: {pivot}",
                "THE RESOLUTION: {resolution}",
                "THE LESSON: {lesson}",
            ],
            "tone": "Narrative and engaging",
        },
        ThreadStructure.COUNTDOWN: {
            "intro": "5 things everyone should know about {topic}. Thread 🧵",
            "structure": [
                "5. {point}",
                "4. {point}",
                "3. {point}",
                "2. {point}",
                "1. The most important: {key_point}",
                "BONUS: {bonus}",
            ],
            "tone": "Punchy and memorable",
        },
        ThreadStructure.LAYERS: {
            "intro": "Let's go deeper on {topic}. Thread 🧵",
            "structure": [
                "SURFACE LEVEL: What most people see about {topic}",
                "ONE LAYER DOWN: The mechanics behind it",
                "DEEPER STILL: The tensions and trade-offs",
                "THE FOUNDATION: The core principle",
                "THE IMPLICATION: What this means for you",
            ],
            "tone": "Progressive revelation",
        },
        ThreadStructure.JOURNEY: {
            "intro": "Come with me on a journey through {topic}. Thread 🧵",
            "structure": [
                "WHERE WE START: Common understanding of {topic}",
                "FIRST STOP: The interesting twist",
                "DETOUR: What people often miss",
                "THE DESTINATION: Deeper understanding",
                "LOOKING BACK: How the view has changed",
            ],
            "tone": "Exploratory and inviting",
        },
        ThreadStructure.COMPARISON: {
            "intro": "{topic}: Expectation vs Reality. Thread 🧵",
            "structure": [
                "What people EXPECT: {expectation}",
                "What actually HAPPENS: {reality}",
                "WHY the gap exists: {explanation}",
                "What this MEANS: {implication}",
                "How to BRIDGE the gap: {action}",
            ],
            "tone": "Clarifying and practical",
        },
    }

    # Closing styles
    CLOSING_VARIANTS = [
        "Something to sit with.",
        "Worth thinking about.",
        "That's the thing about {topic}.",
        "More than you expected from {topic}, right?",
        "The more you know.",
        "Food for thought on {topic}.",
        "And that changes things.",
        "{topic}. Not so simple after all.",
        "Now you know.",
        "Pass it on.",
        "Thoughts?",
        "Agree or disagree?",
    ]

    # Transition phrases between points
    TRANSITIONS = [
        "But here's the thing:",
        "And it gets more interesting:",
        "Plot twist:",
        "Here's where it gets real:",
        "The kicker?",
        "Now, consider this:",
        "But wait:",
        "Here's the part nobody mentions:",
        "The nuance:",
        "Digging deeper:",
    ]

    # Humanization hints for prompts
    HUMANIZATION_HINTS = [
        "Write like you're explaining to a smart friend over coffee",
        "Use contractions naturally - 'it's' not 'it is'",
        "Start with a specific observation, not a general statement",
        "Avoid 'First... Second... Third...' structure",
        "Mix short punchy sentences with longer flowing ones",
        "Don't start with 'It's important to note' or similar cliches",
        "End with something thought-provoking, not a generic CTA",
        "Use one dash or parenthetical for texture",
        "Don't use 'delve', 'unpack', 'robust', or 'leverage'",
        "Sound like a real person, not a press release",
    ]

    def __init__(self, seed: Optional[int] = None):
        """Initialize prompt variants.

        Args:
            seed: Optional random seed for reproducibility.
        """
        if seed is not None:
            random.seed(seed)
        self._used_openings: dict[OpeningStyle, set[str]] = {}
        self._used_structures: set[ThreadStructure] = set()

    def get_tweet_opening(
        self,
        style: Optional[OpeningStyle] = None,
        topic: str = "",
        insight: str = "",
        scenario: str = "",
        misconception: str = "",
        expectation: str = "",
        reality: str = "",
    ) -> str:
        """Get a randomized tweet opening.

        Args:
            style: Optional specific opening style.
            topic: Topic to incorporate.
            insight: Key insight to share.
            scenario: Scenario to describe.
            misconception: Common misconception to address.
            expectation: Expected behavior/outcome.
            reality: Actual behavior/outcome.

        Returns:
            Formatted opening text.
        """
        if style is None:
            style = random.choice(list(OpeningStyle))

        templates = self.TWEET_OPENINGS[style]

        # Try to avoid recently used templates
        used = self._used_openings.get(style, set())
        available = [t for t in templates if t not in used]
        if not available:
            self._used_openings[style] = set()
            available = templates

        template = random.choice(available)
        self._used_openings.setdefault(style, set()).add(template)

        # Format with available parameters
        try:
            return template.format(
                topic=topic,
                insight=insight,
                scenario=scenario,
                misconception=misconception,
                expectation=expectation,
                reality=reality,
            )
        except KeyError:
            # Return template with basic topic substitution if params don't match
            return template.replace("{topic}", topic).replace(
                "{insight}", insight or topic
            )

    def get_thread_structure(
        self,
        structure: Optional[ThreadStructure] = None,
        avoid_recent: bool = True
    ) -> dict:
        """Get a thread structure template.

        Args:
            structure: Optional specific structure.
            avoid_recent: Whether to avoid recently used structures.

        Returns:
            Dict with 'intro', 'structure', and 'tone'.
        """
        if structure is None:
            if avoid_recent:
                available = [s for s in ThreadStructure if s not in self._used_structures]
                if not available:
                    self._used_structures.clear()
                    available = list(ThreadStructure)
                structure = random.choice(available)
            else:
                structure = random.choice(list(ThreadStructure))

        self._used_structures.add(structure)
        return self.THREAD_STRUCTURES[structure].copy()

    def get_closing(self, topic: str = "") -> str:
        """Get a randomized closing phrase.

        Args:
            topic: Topic for personalized closings.

        Returns:
            Closing phrase text.
        """
        closing = random.choice(self.CLOSING_VARIANTS)
        return closing.format(topic=topic) if "{topic}" in closing else closing

    def get_transition(self) -> str:
        """Get a randomized transition phrase."""
        return random.choice(self.TRANSITIONS)

    def get_humanization_hints(self, count: int = 3) -> list[str]:
        """Get random humanization hints for prompt injection.

        Args:
            count: Number of hints to return.

        Returns:
            List of humanization hints.
        """
        return random.sample(
            self.HUMANIZATION_HINTS,
            min(count, len(self.HUMANIZATION_HINTS))
        )

    def get_variant_for_synthesis(
        self,
        synthesis_mode: str,
        topic: str = "",
    ) -> PromptVariant:
        """Get a prompt variant matched to synthesis mode.

        Args:
            synthesis_mode: The synthesis mode (explain, challenge, etc.).
            topic: The topic being synthesized.

        Returns:
            PromptVariant configuration.
        """
        mode_mappings = {
            "explain": (OpeningStyle.OBSERVATION, ThreadStructure.LAYERS),
            "contrast": (OpeningStyle.CONTRAST, ThreadStructure.COMPARISON),
            "challenge": (OpeningStyle.PROVOCATIVE, ThreadStructure.MYTH_REALITY),
            "apply": (OpeningStyle.SCENARIO, ThreadStructure.PROBLEM_SOLUTION),
            "story": (OpeningStyle.SCENARIO, ThreadStructure.STORY_ARC),
            "myth_bust": (OpeningStyle.MISCONCEPTION, ThreadStructure.MYTH_REALITY),
            "implications": (OpeningStyle.SURPRISING_FACT, ThreadStructure.LAYERS),
        }

        opening_style, thread_structure = mode_mappings.get(
            synthesis_mode.lower(),
            (OpeningStyle.OBSERVATION, ThreadStructure.LAYERS)
        )

        thread_config = self.get_thread_structure(thread_structure)
        hints = self.get_humanization_hints(2)

        return PromptVariant(
            name=f"{synthesis_mode}_variant",
            opening_template=self.get_tweet_opening(
                style=opening_style,
                topic=topic,
            ),
            structure_hint=str(thread_config.get("structure", [])),
            tone_guidance=thread_config.get("tone", "Conversational and engaging"),
            closing_style=self.get_closing(topic),
        )

    def build_synthesis_prompt_additions(
        self,
        synthesis_mode: str,
        topic: str = "",
    ) -> str:
        """Build additional prompt text for synthesis.

        Args:
            synthesis_mode: The synthesis mode.
            topic: The topic being synthesized.

        Returns:
            Additional prompt text.
        """
        variant = self.get_variant_for_synthesis(synthesis_mode, topic)
        hints = self.get_humanization_hints(3)

        additions = [
            "\n## Writing Style Guidance:",
            f"- Tone: {variant.tone_guidance}",
            f"- Consider opening with: '{variant.opening_template}'",
            f"- Closing style: {variant.closing_style}",
            "",
            "## Human-Like Writing Tips:",
        ]
        additions.extend(f"- {hint}" for hint in hints)

        return "\n".join(additions)

    def clear_used_variants(self) -> None:
        """Clear tracked used variants."""
        self._used_openings.clear()
        self._used_structures.clear()

    def get_all_opening_styles(self) -> list[OpeningStyle]:
        """Get all available opening styles."""
        return list(OpeningStyle)

    def get_all_thread_structures(self) -> list[ThreadStructure]:
        """Get all available thread structures."""
        return list(ThreadStructure)
