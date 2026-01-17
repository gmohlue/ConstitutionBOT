"""AI Pattern Detection and Filtering Module.

This module detects and filters AI-typical writing patterns to produce
more natural, human-like content.
"""

import random
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PatternCategory(Enum):
    """Categories of AI writing patterns."""

    CLICHE_OPENER = "cliche_opener"
    CLICHE_PHRASE = "cliche_phrase"
    HEDGING = "hedging"
    LIST_STRUCTURE = "list_structure"
    MIRROR_STRUCTURE = "mirror_structure"
    CORPORATE_SPEAK = "corporate_speak"
    FILLER_WORDS = "filler_words"
    PASSIVE_VOICE = "passive_voice"


@dataclass
class DetectedPattern:
    """A detected AI writing pattern."""

    category: PatternCategory
    matched_text: str
    position: tuple[int, int]  # start, end
    severity: float  # 0.0 to 1.0
    suggestion: Optional[str] = None


@dataclass
class AIPatternReport:
    """Report of AI pattern analysis."""

    content: str
    patterns: list[DetectedPattern] = field(default_factory=list)
    ai_score: float = 0.0  # 0.0 (human) to 1.0 (AI)
    sentence_variance: float = 0.0  # Higher is more varied
    suggestions: list[str] = field(default_factory=list)

    @property
    def is_human_like(self) -> bool:
        """Check if content passes human-likeness threshold."""
        return self.ai_score < 0.5

    @property
    def pattern_count(self) -> int:
        """Total number of detected patterns."""
        return len(self.patterns)


class AIPatternFilter:
    """Detects and filters AI-typical writing patterns."""

    # Cliche openers that AI models commonly use
    CLICHE_OPENERS = [
        r"^It'?s important to (note|remember|understand|recognize)",
        r"^In today'?s (world|society|age|digital age)",
        r"^Let'?s (delve|dive|explore|unpack|break down)",
        r"^When it comes to",
        r"^In (this|the) (article|post|thread|piece)",
        r"^(Have you ever|Did you know)",
        r"^(First and foremost|First off|To begin with)",
        r"^(Interestingly|Surprisingly|Remarkably|Notably)",
        r"^As (we all know|many know|you may know)",
        r"^The (truth|reality|fact) is",
        r"^(Here'?s|This is) (why|how|what)",
        r"^(Whether you|If you)'?re (new to|familiar with)",
    ]

    # Cliche phrases used throughout content
    CLICHE_PHRASES = [
        r"at the end of the day",
        r"it goes without saying",
        r"needless to say",
        r"in (this|today'?s) day and age",
        r"the bottom line is",
        r"when all is said and done",
        r"last but not least",
        r"in a nutshell",
        r"time will tell",
        r"only time will tell",
        r"the fact (of the matter|remains) (is|that)",
        r"it'?s worth (noting|mentioning|pointing out)",
        r"plays a (crucial|vital|key|important|significant) role",
        r"(crucial|vital|key|important|significant) (to note|to remember|to understand)",
        r"(serves|acts) as a (reminder|testament)",
        r"paves the way",
        r"stands as a testament",
        r"food for thought",
        r"game changer",
        r"a double-edged sword",
    ]

    # Hedging language that weakens writing
    HEDGING_PATTERNS = [
        r"\b(perhaps|maybe|possibly|potentially)\b",
        r"\bit (could|might|may) be (said|argued|noted)",
        r"\bto some (extent|degree)\b",
        r"\bin some (ways|respects)\b",
        r"\bit'?s (possible|likely|probable) that\b",
        r"\bthere (is|are) (some|a) (debate|discussion|argument)",
        r"\bone (could|might|may) argue",
        r"\bit (seems|appears) (that|to be)",
        r"\bgenerally speaking\b",
        r"\bfor the most part\b",
    ]

    # Corporate/AI buzzwords to avoid
    CORPORATE_SPEAK = [
        r"\bdelve\b",
        r"\bunpack\b",
        r"\brobust\b",
        r"\bleverage\b",
        r"\bsynerg(y|ize|istic)\b",
        r"\bholistic\b",
        r"\bparadigm\b",
        r"\bpivot\b",
        r"\bscalable\b",
        r"\binnovative\b",
        r"\bimpactful\b",
        r"\bactionable\b",
        r"\bempower(ing|ment|ed)?\b",
        r"\btransform(ative|ational)\b",
        r"\bcutting-?edge\b",
        r"\bsolution\b",
        r"\becosystem\b",
        r"\bstakeholder\b",
        r"\bbest practice\b",
        r"\bvalue-?add(ed)?\b",
        r"\bthought leader(ship)?\b",
        r"\bdisrupt(ive|ion)?\b",
    ]

    # Filler phrases that add no value
    FILLER_PATTERNS = [
        r"\bbasically\b",
        r"\bactually\b",
        r"\bessentially\b",
        r"\bfundamentally\b",
        r"\bobviously\b",
        r"\bclearly\b",
        r"\bcertainly\b",
        r"\bdefinitely\b",
        r"\babsolutely\b",
        r"\bliterally\b",
        r"\bvery\b",
        r"\breally\b",
        r"\bquite\b",
        r"\brather\b",
        r"\bsimply\b",
        r"\bjust\b",
    ]

    # List structure patterns
    LIST_PATTERNS = [
        r"^(First|Firstly|1\.|1\)),?\s",
        r"^(Second|Secondly|2\.|2\)),?\s",
        r"^(Third|Thirdly|3\.|3\)),?\s",
        r"(First|Firstly)[,.].*?(Second|Secondly)[,.].*?(Third|Thirdly)",
    ]

    # Generic call-to-action endings
    GENERIC_CTA = [
        r"(What do you think|Share your thoughts|Let (me|us) know)",
        r"(Stay tuned|Stay connected|Follow for more)",
        r"(Don'?t forget to|Remember to|Be sure to) (like|share|subscribe|follow)",
        r"(Together|Collectively),? we can",
        r"(Start|Begin) your journey",
        r"Take the (first|next) step",
        r"Join (us|the conversation|the movement)",
        r"Make (a|the) (difference|change)",
    ]

    # Alternative openers to suggest
    ALTERNATIVE_OPENERS = [
        "Start with a specific observation or fact",
        "Begin mid-thought with context",
        "Open with a brief scenario",
        "Lead with a surprising statistic",
        "Start with a question that challenges assumptions",
        "Open with a concrete example",
        "Begin with a short anecdote",
    ]

    # Human-like sentence starters
    HUMAN_STARTERS = [
        "So here's the thing:",
        "Picture this:",
        "There's this moment when",
        "You know how",
        "Ever notice how",
        "Something people miss:",
        "Real talk:",
        "Funny thing about",
        "The quiet truth:",
        "Here's what nobody tells you:",
        "Quick thought:",
        "Something I've been thinking about:",
    ]

    def __init__(self, strict_mode: bool = False):
        """Initialize the AI pattern filter.

        Args:
            strict_mode: If True, apply stricter pattern detection.
        """
        self.strict_mode = strict_mode
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency."""
        flags = re.IGNORECASE | re.MULTILINE

        self._opener_patterns = [
            re.compile(p, flags) for p in self.CLICHE_OPENERS
        ]
        self._cliche_patterns = [
            re.compile(p, flags) for p in self.CLICHE_PHRASES
        ]
        self._hedging_patterns = [
            re.compile(p, flags) for p in self.HEDGING_PATTERNS
        ]
        self._corporate_patterns = [
            re.compile(p, flags) for p in self.CORPORATE_SPEAK
        ]
        self._filler_patterns = [
            re.compile(p, flags) for p in self.FILLER_PATTERNS
        ]
        self._list_patterns = [
            re.compile(p, flags) for p in self.LIST_PATTERNS
        ]
        self._cta_patterns = [
            re.compile(p, flags) for p in self.GENERIC_CTA
        ]

    def analyze(self, content: str) -> AIPatternReport:
        """Analyze content for AI writing patterns.

        Args:
            content: The text content to analyze.

        Returns:
            AIPatternReport with detected patterns and scores.
        """
        patterns: list[DetectedPattern] = []

        # Detect cliche openers
        patterns.extend(self._detect_cliche_openers(content))

        # Detect cliche phrases
        patterns.extend(self._detect_cliche_phrases(content))

        # Detect hedging
        patterns.extend(self._detect_hedging(content))

        # Detect corporate speak
        patterns.extend(self._detect_corporate_speak(content))

        # Detect filler words
        if self.strict_mode:
            patterns.extend(self._detect_filler_words(content))

        # Detect list structures
        patterns.extend(self._detect_list_structures(content))

        # Detect generic CTAs
        patterns.extend(self._detect_generic_cta(content))

        # Calculate metrics
        ai_score = self._calculate_ai_score(content, patterns)
        sentence_variance = self._calculate_sentence_variance(content)
        suggestions = self._generate_suggestions(patterns, sentence_variance)

        return AIPatternReport(
            content=content,
            patterns=patterns,
            ai_score=ai_score,
            sentence_variance=sentence_variance,
            suggestions=suggestions
        )

    def _detect_cliche_openers(self, content: str) -> list[DetectedPattern]:
        """Detect cliche opening phrases."""
        patterns = []
        for pattern in self._opener_patterns:
            for match in pattern.finditer(content):
                patterns.append(DetectedPattern(
                    category=PatternCategory.CLICHE_OPENER,
                    matched_text=match.group(),
                    position=(match.start(), match.end()),
                    severity=0.8,
                    suggestion=random.choice(self.ALTERNATIVE_OPENERS)
                ))
        return patterns

    def _detect_cliche_phrases(self, content: str) -> list[DetectedPattern]:
        """Detect cliche phrases throughout content."""
        patterns = []
        for pattern in self._cliche_patterns:
            for match in pattern.finditer(content):
                patterns.append(DetectedPattern(
                    category=PatternCategory.CLICHE_PHRASE,
                    matched_text=match.group(),
                    position=(match.start(), match.end()),
                    severity=0.6,
                    suggestion="Remove or rephrase with concrete language"
                ))
        return patterns

    def _detect_hedging(self, content: str) -> list[DetectedPattern]:
        """Detect hedging language."""
        patterns = []
        hedging_count = 0
        for pattern in self._hedging_patterns:
            for match in pattern.finditer(content):
                hedging_count += 1
                if hedging_count > 2 or self.strict_mode:  # Allow some hedging
                    patterns.append(DetectedPattern(
                        category=PatternCategory.HEDGING,
                        matched_text=match.group(),
                        position=(match.start(), match.end()),
                        severity=0.4,
                        suggestion="Consider being more direct"
                    ))
        return patterns

    def _detect_corporate_speak(self, content: str) -> list[DetectedPattern]:
        """Detect corporate/AI buzzwords."""
        patterns = []
        for pattern in self._corporate_patterns:
            for match in pattern.finditer(content):
                patterns.append(DetectedPattern(
                    category=PatternCategory.CORPORATE_SPEAK,
                    matched_text=match.group(),
                    position=(match.start(), match.end()),
                    severity=0.7,
                    suggestion=f"Replace '{match.group()}' with simpler language"
                ))
        return patterns

    def _detect_filler_words(self, content: str) -> list[DetectedPattern]:
        """Detect filler words (only in strict mode)."""
        patterns = []
        for pattern in self._filler_patterns:
            for match in pattern.finditer(content):
                patterns.append(DetectedPattern(
                    category=PatternCategory.FILLER_WORDS,
                    matched_text=match.group(),
                    position=(match.start(), match.end()),
                    severity=0.2,
                    suggestion="Consider removing this filler word"
                ))
        return patterns

    def _detect_list_structures(self, content: str) -> list[DetectedPattern]:
        """Detect AI-typical list structures."""
        patterns = []
        for pattern in self._list_patterns:
            for match in pattern.finditer(content):
                patterns.append(DetectedPattern(
                    category=PatternCategory.LIST_STRUCTURE,
                    matched_text=match.group(),
                    position=(match.start(), match.end()),
                    severity=0.5,
                    suggestion="Consider varying the structure"
                ))
        return patterns

    def _detect_generic_cta(self, content: str) -> list[DetectedPattern]:
        """Detect generic call-to-action endings."""
        patterns = []
        for pattern in self._cta_patterns:
            for match in pattern.finditer(content):
                patterns.append(DetectedPattern(
                    category=PatternCategory.CLICHE_PHRASE,
                    matched_text=match.group(),
                    position=(match.start(), match.end()),
                    severity=0.6,
                    suggestion="End with a thought-provoking angle instead"
                ))
        return patterns

    def _calculate_ai_score(
        self,
        content: str,
        patterns: list[DetectedPattern]
    ) -> float:
        """Calculate overall AI likelihood score.

        Args:
            content: The original content.
            patterns: Detected patterns.

        Returns:
            Score from 0.0 (human-like) to 1.0 (AI-like).
        """
        if not content.strip():
            return 0.0

        # Base score from pattern count and severity
        total_severity = sum(p.severity for p in patterns)
        word_count = len(content.split())

        # Normalize by content length
        pattern_score = min(total_severity / max(word_count / 10, 1), 1.0)

        # Check sentence variance (uniform sentences are more AI-like)
        variance_score = self._calculate_sentence_variance(content)
        variance_penalty = max(0, 0.3 - variance_score) * 2  # Penalty for low variance

        # Check for cliche openers (heavy penalty)
        opener_patterns = [p for p in patterns if p.category == PatternCategory.CLICHE_OPENER]
        opener_penalty = 0.3 if opener_patterns else 0.0

        # Combine scores
        ai_score = min(pattern_score + variance_penalty + opener_penalty, 1.0)

        return round(ai_score, 3)

    def _calculate_sentence_variance(self, content: str) -> float:
        """Calculate sentence length variance.

        Higher variance indicates more natural, human writing.

        Args:
            content: The text to analyze.

        Returns:
            Variance score from 0.0 to 1.0.
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.5  # Can't measure variance with one sentence

        # Calculate word counts
        word_counts = [len(s.split()) for s in sentences]

        if not word_counts:
            return 0.0

        # Calculate coefficient of variation (normalized variance)
        mean = sum(word_counts) / len(word_counts)
        if mean == 0:
            return 0.0

        variance = sum((x - mean) ** 2 for x in word_counts) / len(word_counts)
        std_dev = variance ** 0.5
        cv = std_dev / mean

        # Normalize to 0-1 range (CV of 0.5 is considered ideal)
        # Higher variance (up to a point) is more human-like
        variance_score = min(cv / 0.5, 1.0)

        return round(variance_score, 3)

    def _generate_suggestions(
        self,
        patterns: list[DetectedPattern],
        sentence_variance: float
    ) -> list[str]:
        """Generate improvement suggestions based on detected patterns.

        Args:
            patterns: Detected AI patterns.
            sentence_variance: Sentence length variance score.

        Returns:
            List of improvement suggestions.
        """
        suggestions = []

        # Count patterns by category
        category_counts = {}
        for p in patterns:
            category_counts[p.category] = category_counts.get(p.category, 0) + 1

        # Generate category-specific suggestions
        if PatternCategory.CLICHE_OPENER in category_counts:
            suggestions.append(
                "Start with a specific observation, question, or mid-thought opener"
            )

        if category_counts.get(PatternCategory.CLICHE_PHRASE, 0) > 1:
            suggestions.append(
                "Replace cliche phrases with concrete, specific language"
            )

        if category_counts.get(PatternCategory.HEDGING, 0) > 2:
            suggestions.append(
                "Reduce hedging language - be more direct and confident"
            )

        if PatternCategory.CORPORATE_SPEAK in category_counts:
            suggestions.append(
                "Replace buzzwords with simpler, everyday words"
            )

        if PatternCategory.LIST_STRUCTURE in category_counts:
            suggestions.append(
                "Vary the structure - avoid First/Second/Third patterns"
            )

        # Sentence variance suggestions
        if sentence_variance < 0.3:
            suggestions.append(
                "Mix sentence lengths: combine short punchy sentences with longer flowing ones"
            )

        return suggestions

    def humanize(self, content: str) -> str:
        """Apply automatic humanization to content.

        Args:
            content: Content to humanize.

        Returns:
            Humanized content with patterns filtered.
        """
        result = content

        # Replace common cliche openers
        opener_replacements = [
            (r"^It'?s important to (note|remember|understand) that ", ""),
            (r"^In today'?s (world|society|age), ", ""),
            (r"^Let'?s (delve|dive) into ", ""),
            (r"^When it comes to ([^,]+), ", r"\1: "),
        ]

        for pattern, replacement in opener_replacements:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # Replace corporate buzzwords
        buzzword_replacements = {
            r"\bleverage\b": "use",
            r"\butilize\b": "use",
            r"\bimpactful\b": "effective",
            r"\brobust\b": "strong",
            r"\bholistic\b": "complete",
            r"\bsynergy\b": "collaboration",
            r"\bparadigm\b": "model",
            r"\bactionable\b": "practical",
            r"\bempowering\b": "enabling",
            r"\btransformative\b": "changing",
        }

        for pattern, replacement in buzzword_replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # Add contractions for a more natural feel
        contraction_map = {
            r"\bit is\b": "it's",
            r"\bthat is\b": "that's",
            r"\bwhat is\b": "what's",
            r"\bdo not\b": "don't",
            r"\bdoes not\b": "doesn't",
            r"\bcannot\b": "can't",
            r"\bwill not\b": "won't",
            r"\bthey are\b": "they're",
            r"\bwe are\b": "we're",
            r"\byou are\b": "you're",
            r"\bI am\b": "I'm",
            r"\bI have\b": "I've",
            r"\bI would\b": "I'd",
            r"\bwould not\b": "wouldn't",
            r"\bcould not\b": "couldn't",
            r"\bshould not\b": "shouldn't",
        }

        for pattern, replacement in contraction_map.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result

    def get_random_human_starter(self) -> str:
        """Get a random human-like sentence starter."""
        return random.choice(self.HUMAN_STARTERS)

    def validate_human_likeness(
        self,
        content: str,
        threshold: float = 0.5
    ) -> tuple[bool, AIPatternReport]:
        """Validate content passes human-likeness threshold.

        Args:
            content: Content to validate.
            threshold: Maximum allowed AI score (default 0.5).

        Returns:
            Tuple of (is_valid, report).
        """
        report = self.analyze(content)
        is_valid = report.ai_score <= threshold
        return is_valid, report
