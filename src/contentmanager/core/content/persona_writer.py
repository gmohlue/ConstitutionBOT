"""Human Voice Layer Module.

This module applies human writing characteristics and persona-based
transformations to make content sound more natural and authentic.
"""

import random
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ToneType(Enum):
    """Types of writing tones."""

    CONVERSATIONAL = "conversational"
    THOUGHTFUL = "thoughtful"
    ENERGETIC = "energetic"
    SERIOUS = "serious"
    WARM = "warm"
    DIRECT = "direct"


class RhetoricalStyle(Enum):
    """Rhetorical styles for persuasion."""

    SOCRATIC = "socratic"  # Questions that lead to insight
    NARRATIVE = "narrative"  # Story-driven
    DIRECT = "direct"  # Straightforward statements
    EXPLORATORY = "exploratory"  # Thinking out loud
    PROVOCATIVE = "provocative"  # Challenge assumptions


@dataclass
class WritingPersona:
    """A writing persona with specific characteristics."""

    name: str
    tone: ToneType
    formality_level: float = 0.5  # 0.0 (casual) to 1.0 (formal)
    uses_contractions: bool = True
    rhetorical_style: RhetoricalStyle = RhetoricalStyle.DIRECT
    personality_words: list[str] = field(default_factory=list)
    avoided_words: list[str] = field(default_factory=list)

    # Writing patterns
    prefers_short_sentences: bool = False
    uses_rhetorical_questions: bool = True
    uses_em_dashes: bool = True
    uses_parentheticals: bool = True
    sentence_start_variety: bool = True

    def to_prompt_description(self) -> str:
        """Generate description for prompt injection."""
        parts = [
            f"Voice: {self.tone.value}",
            f"Formality: {'formal' if self.formality_level > 0.6 else 'casual' if self.formality_level < 0.4 else 'balanced'}",
            f"Style: {self.rhetorical_style.value}",
        ]

        if self.uses_contractions:
            parts.append("Uses contractions naturally")
        else:
            parts.append("Avoids contractions")

        if self.personality_words:
            parts.append(f"Characteristic vocabulary: {', '.join(self.personality_words[:5])}")

        if self.avoided_words:
            parts.append(f"Never uses: {', '.join(self.avoided_words[:5])}")

        return "; ".join(parts)


# Pre-built personas
PERSONAS = {
    "conversational": WritingPersona(
        name="Conversational Educator",
        tone=ToneType.CONVERSATIONAL,
        formality_level=0.3,
        uses_contractions=True,
        rhetorical_style=RhetoricalStyle.EXPLORATORY,
        personality_words=["actually", "here's the thing", "so", "look", "honestly"],
        avoided_words=["furthermore", "moreover", "thus", "hence", "whereby"],
        prefers_short_sentences=True,
        uses_rhetorical_questions=True,
        uses_em_dashes=True,
        uses_parentheticals=True,
    ),
    "thoughtful": WritingPersona(
        name="Thoughtful Analyst",
        tone=ToneType.THOUGHTFUL,
        formality_level=0.5,
        uses_contractions=True,
        rhetorical_style=RhetoricalStyle.SOCRATIC,
        personality_words=["consider", "perhaps", "interestingly", "notably", "worth noting"],
        avoided_words=["obviously", "clearly", "undoubtedly"],
        prefers_short_sentences=False,
        uses_rhetorical_questions=True,
        uses_em_dashes=True,
        uses_parentheticals=True,
    ),
    "energetic": WritingPersona(
        name="Energetic Advocate",
        tone=ToneType.ENERGETIC,
        formality_level=0.2,
        uses_contractions=True,
        rhetorical_style=RhetoricalStyle.PROVOCATIVE,
        personality_words=["wow", "seriously", "huge", "game-changer", "wild"],
        avoided_words=["perhaps", "maybe", "somewhat", "rather"],
        prefers_short_sentences=True,
        uses_rhetorical_questions=True,
        uses_em_dashes=True,
        uses_parentheticals=False,
    ),
    "serious": WritingPersona(
        name="Serious Scholar",
        tone=ToneType.SERIOUS,
        formality_level=0.7,
        uses_contractions=False,
        rhetorical_style=RhetoricalStyle.DIRECT,
        personality_words=["significant", "essential", "critical", "fundamental"],
        avoided_words=["kind of", "sort of", "basically", "like"],
        prefers_short_sentences=False,
        uses_rhetorical_questions=False,
        uses_em_dashes=False,
        uses_parentheticals=False,
    ),
    "warm": WritingPersona(
        name="Warm Guide",
        tone=ToneType.WARM,
        formality_level=0.4,
        uses_contractions=True,
        rhetorical_style=RhetoricalStyle.NARRATIVE,
        personality_words=["together", "we", "our", "let's", "imagine"],
        avoided_words=["you must", "you should", "failure", "wrong"],
        prefers_short_sentences=False,
        uses_rhetorical_questions=True,
        uses_em_dashes=True,
        uses_parentheticals=True,
    ),
    "direct": WritingPersona(
        name="Direct Communicator",
        tone=ToneType.DIRECT,
        formality_level=0.5,
        uses_contractions=True,
        rhetorical_style=RhetoricalStyle.DIRECT,
        personality_words=["here's", "bottom line", "simply", "plain"],
        avoided_words=["perhaps", "maybe", "might", "could be"],
        prefers_short_sentences=True,
        uses_rhetorical_questions=False,
        uses_em_dashes=False,
        uses_parentheticals=False,
    ),
}


@dataclass
class HumanizationResult:
    """Result of humanization transformation."""

    original: str
    transformed: str
    changes_made: list[str]
    persona_applied: Optional[str] = None


class PersonaWriter:
    """Applies human writing characteristics to content."""

    # Contractions map
    CONTRACTION_MAP = {
        "it is": "it's",
        "that is": "that's",
        "what is": "what's",
        "there is": "there's",
        "here is": "here's",
        "do not": "don't",
        "does not": "doesn't",
        "did not": "didn't",
        "cannot": "can't",
        "could not": "couldn't",
        "would not": "wouldn't",
        "should not": "shouldn't",
        "will not": "won't",
        "is not": "isn't",
        "are not": "aren't",
        "was not": "wasn't",
        "were not": "weren't",
        "have not": "haven't",
        "has not": "hasn't",
        "had not": "hadn't",
        "they are": "they're",
        "we are": "we're",
        "you are": "you're",
        "I am": "I'm",
        "I have": "I've",
        "I had": "I'd",
        "I would": "I'd",
        "I will": "I'll",
        "you have": "you've",
        "you will": "you'll",
        "we have": "we've",
        "we will": "we'll",
        "they have": "they've",
        "they will": "they'll",
        "let us": "let's",
    }

    # Human-like imperfections to add variety
    IMPERFECTION_PATTERNS = [
        (" - ", " — "),  # Em dash
        (". ", ". And "),  # Occasional conjunction start
        (", and ", " — and "),  # Em dash variation
        (". This ", ". (This "),  # Parenthetical aside
        ("because ", "because — "),  # Pause for effect
    ]

    # Sentence starters for variety
    VARIED_STARTERS = [
        "And ",
        "But ",
        "So ",
        "Now ",
        "See, ",
        "Thing is, ",
        "Point being, ",
        "Here's what: ",
        "Quick note: ",
        "Real talk: ",
    ]

    # Filler removers
    FILLER_WORDS = [
        r"\bbasically\b",
        r"\bactually\b",
        r"\bessentially\b",
        r"\bfundamentally\b",
        r"\bin terms of\b",
        r"\bat this point in time\b",
        r"\bin order to\b",
        r"\bdue to the fact that\b",
    ]

    def __init__(self, default_persona: str = "conversational"):
        """Initialize the persona writer.

        Args:
            default_persona: Name of the default persona to use.
        """
        self.default_persona = PERSONAS.get(default_persona, PERSONAS["conversational"])

    def humanize_content(
        self,
        content: str,
        persona: Optional[WritingPersona] = None
    ) -> HumanizationResult:
        """Apply human writing transformations to content.

        Args:
            content: Content to humanize.
            persona: Optional persona to apply.

        Returns:
            HumanizationResult with transformed content.
        """
        persona = persona or self.default_persona
        changes = []
        result = content

        # Apply contractions if persona allows
        if persona.uses_contractions:
            result, contraction_changes = self._apply_contractions(result)
            changes.extend(contraction_changes)

        # Vary sentence structure
        if persona.sentence_start_variety:
            result, variety_changes = self._vary_sentence_starts(result)
            changes.extend(variety_changes)

        # Add imperfections based on persona
        if persona.uses_em_dashes or persona.uses_parentheticals:
            result, imperfection_changes = self._add_imperfections(result, persona)
            changes.extend(imperfection_changes)

        # Apply persona-specific vocabulary
        result, vocab_changes = self._apply_persona_vocabulary(result, persona)
        changes.extend(vocab_changes)

        # Remove filler words
        result, filler_changes = self._remove_fillers(result)
        changes.extend(filler_changes)

        # Final polish
        result = self._final_polish(result)

        return HumanizationResult(
            original=content,
            transformed=result,
            changes_made=changes,
            persona_applied=persona.name
        )

    def apply_voice(
        self,
        content: str,
        persona: Optional[WritingPersona] = None
    ) -> str:
        """Apply persona's voice to content.

        Args:
            content: Content to transform.
            persona: Persona to apply.

        Returns:
            Content with voice applied.
        """
        persona = persona or self.default_persona
        result = content

        # Adjust formality
        if persona.formality_level < 0.4:
            result = self._make_casual(result)
        elif persona.formality_level > 0.6:
            result = self._make_formal(result)

        # Apply rhetorical style
        if persona.rhetorical_style == RhetoricalStyle.SOCRATIC:
            result = self._add_socratic_elements(result)
        elif persona.rhetorical_style == RhetoricalStyle.NARRATIVE:
            result = self._add_narrative_elements(result)
        elif persona.rhetorical_style == RhetoricalStyle.PROVOCATIVE:
            result = self._add_provocative_elements(result)

        return result

    def vary_sentence_structure(self, content: str) -> str:
        """Vary sentence lengths and structures.

        Args:
            content: Content to vary.

        Returns:
            Content with varied structure.
        """
        sentences = self._split_sentences(content)
        if len(sentences) < 2:
            return content

        result_sentences = []
        for i, sentence in enumerate(sentences):
            words = sentence.split()

            # Occasionally make short punchy sentences
            if len(words) > 15 and random.random() < 0.3:
                # Split long sentence
                midpoint = len(words) // 2
                for j in range(midpoint - 3, midpoint + 3):
                    if j < len(words) and words[j] in ["and", "but", "which", "that"]:
                        first_part = " ".join(words[:j])
                        second_part = " ".join(words[j + 1:]).capitalize()
                        result_sentences.append(first_part + ".")
                        result_sentences.append(second_part)
                        break
                else:
                    result_sentences.append(sentence)
            # Occasionally combine short sentences
            elif len(words) < 8 and i < len(sentences) - 1:
                next_sentence = sentences[i + 1]
                if len(next_sentence.split()) < 8:
                    combined = sentence.rstrip(".") + " — " + next_sentence.lower()
                    result_sentences.append(combined)
                    sentences[i + 1] = ""  # Mark as used
                else:
                    result_sentences.append(sentence)
            else:
                result_sentences.append(sentence)

        return " ".join(s for s in result_sentences if s)

    def get_persona(self, name: str) -> Optional[WritingPersona]:
        """Get a persona by name.

        Args:
            name: Persona name.

        Returns:
            WritingPersona if found, else None.
        """
        return PERSONAS.get(name)

    def list_personas(self) -> list[str]:
        """List all available persona names."""
        return list(PERSONAS.keys())

    # Private transformation methods

    def _apply_contractions(self, content: str) -> tuple[str, list[str]]:
        """Apply natural contractions."""
        changes = []
        result = content

        for full, contracted in self.CONTRACTION_MAP.items():
            pattern = re.compile(re.escape(full), re.IGNORECASE)
            if pattern.search(result):
                result = pattern.sub(contracted, result)
                changes.append(f"Contracted '{full}' → '{contracted}'")

        return result, changes

    def _vary_sentence_starts(self, content: str) -> tuple[str, list[str]]:
        """Add variety to sentence starts."""
        changes = []
        sentences = self._split_sentences(content)

        if len(sentences) < 3:
            return content, changes

        # Check for repetitive starts
        starts = [s.split()[0].lower() if s.split() else "" for s in sentences]
        repetitive = any(starts.count(s) > 2 for s in set(starts))

        if repetitive:
            result_sentences = []
            for i, sentence in enumerate(sentences):
                if i > 0 and random.random() < 0.2:
                    starter = random.choice(self.VARIED_STARTERS)
                    # Don't add if sentence already starts informally
                    if not sentence[0].islower():
                        sentence = starter + sentence[0].lower() + sentence[1:]
                        changes.append(f"Added varied starter: '{starter}'")
                result_sentences.append(sentence)
            return " ".join(result_sentences), changes

        return content, changes

    def _add_imperfections(
        self,
        content: str,
        persona: WritingPersona
    ) -> tuple[str, list[str]]:
        """Add human-like imperfections."""
        changes = []
        result = content

        # Add one imperfection at random
        if random.random() < 0.4:
            pattern, replacement = random.choice(self.IMPERFECTION_PATTERNS)

            # Only add em dashes if persona allows
            if "—" in replacement and not persona.uses_em_dashes:
                return result, changes

            # Only add parentheticals if persona allows
            if "(" in replacement and not persona.uses_parentheticals:
                return result, changes

            if pattern in result:
                # Only replace one occurrence
                result = result.replace(pattern, replacement, 1)
                changes.append(f"Added imperfection: '{pattern}' → '{replacement}'")

        return result, changes

    def _apply_persona_vocabulary(
        self,
        content: str,
        persona: WritingPersona
    ) -> tuple[str, list[str]]:
        """Apply persona-specific vocabulary."""
        changes = []
        result = content

        # Remove avoided words
        for avoided in persona.avoided_words:
            pattern = re.compile(r"\b" + re.escape(avoided) + r"\b", re.IGNORECASE)
            if pattern.search(result):
                result = pattern.sub("", result)
                changes.append(f"Removed avoided word: '{avoided}'")

        # Clean up double spaces
        result = re.sub(r"\s+", " ", result)

        return result, changes

    def _remove_fillers(self, content: str) -> tuple[str, list[str]]:
        """Remove filler words and phrases."""
        changes = []
        result = content

        for pattern in self.FILLER_WORDS:
            regex = re.compile(pattern, re.IGNORECASE)
            if regex.search(result):
                result = regex.sub("", result)
                changes.append(f"Removed filler: '{pattern}'")

        # Clean up
        result = re.sub(r"\s+", " ", result)
        return result, changes

    def _make_casual(self, content: str) -> str:
        """Make content more casual."""
        result = content

        # Apply all contractions
        for full, contracted in self.CONTRACTION_MAP.items():
            result = re.sub(
                re.escape(full),
                contracted,
                result,
                flags=re.IGNORECASE
            )

        # Add casual transitions
        casual_replacements = {
            "However,": "But",
            "Therefore,": "So",
            "Furthermore,": "Also,",
            "Nevertheless,": "Still,",
            "Additionally,": "Plus,",
        }

        for formal, casual in casual_replacements.items():
            result = result.replace(formal, casual)

        return result

    def _make_formal(self, content: str) -> str:
        """Make content more formal."""
        result = content

        # Expand contractions
        reverse_contractions = {v: k for k, v in self.CONTRACTION_MAP.items()}
        for contracted, full in reverse_contractions.items():
            result = re.sub(
                re.escape(contracted),
                full,
                result,
                flags=re.IGNORECASE
            )

        # Replace casual words
        formal_replacements = {
            "But ": "However, ",
            "So ": "Therefore, ",
            "Also,": "Furthermore,",
            "Plus,": "Additionally,",
        }

        for casual, formal in formal_replacements.items():
            result = result.replace(casual, formal)

        return result

    def _add_socratic_elements(self, content: str) -> str:
        """Add Socratic questioning elements."""
        sentences = self._split_sentences(content)
        if len(sentences) < 2:
            return content

        # Add a question near the beginning
        questions = [
            "But what does this really mean?",
            "Consider: what are the implications?",
            "Ask yourself: when would this matter?",
            "The question becomes: how does this apply?",
        ]

        # Insert after first or second sentence
        insert_pos = min(1, len(sentences) - 1)
        sentences.insert(insert_pos + 1, random.choice(questions))

        return " ".join(sentences)

    def _add_narrative_elements(self, content: str) -> str:
        """Add narrative storytelling elements."""
        # Add a narrative opener if not present
        narrative_openers = [
            "Picture this: ",
            "Here's how it plays out: ",
            "The story goes like this: ",
            "Imagine the scenario: ",
        ]

        if not any(opener in content for opener in narrative_openers):
            return random.choice(narrative_openers) + content

        return content

    def _add_provocative_elements(self, content: str) -> str:
        """Add provocative, challenging elements."""
        # Add a provocative starter
        provocative_starters = [
            "Here's what nobody's telling you: ",
            "Uncomfortable truth: ",
            "Let's be real here: ",
            "The part they leave out: ",
        ]

        if not any(s in content for s in provocative_starters):
            return random.choice(provocative_starters) + content

        return content

    def _split_sentences(self, content: str) -> list[str]:
        """Split content into sentences."""
        # Handle common abbreviations
        content = content.replace("Mr.", "Mr")
        content = content.replace("Mrs.", "Mrs")
        content = content.replace("Dr.", "Dr")
        content = content.replace("vs.", "vs")
        content = content.replace("etc.", "etc")
        content = content.replace("i.e.", "ie")
        content = content.replace("e.g.", "eg")

        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Restore abbreviations
        restored = []
        for s in sentences:
            s = s.replace("Mr", "Mr.")
            s = s.replace("Mrs", "Mrs.")
            s = s.replace("Dr", "Dr.")
            s = s.replace("vs", "vs.")
            s = s.replace("etc", "etc.")
            s = s.replace("ie", "i.e.")
            s = s.replace("eg", "e.g.")
            restored.append(s)

        return restored

    def _final_polish(self, content: str) -> str:
        """Final cleanup and polish."""
        result = content

        # Fix double spaces
        result = re.sub(r"\s+", " ", result)

        # Fix punctuation spacing
        result = re.sub(r"\s+([.,!?])", r"\1", result)
        result = re.sub(r"([.,!?])([A-Z])", r"\1 \2", result)

        # Ensure ending punctuation
        if result and result[-1] not in ".!?":
            result += "."

        return result.strip()


def get_default_personas() -> dict[str, WritingPersona]:
    """Get all default personas."""
    return PERSONAS.copy()
