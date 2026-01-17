"""Insight Analysis Module.

This module analyzes document sections to extract deep insights,
core principles, and practical meanings for content synthesis.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.database.models import DocumentSection


class InsightType(Enum):
    """Types of insights that can be extracted."""

    CORE_PRINCIPLE = "core_principle"
    PRACTICAL_APPLICATION = "practical_application"
    COMMON_MISCONCEPTION = "common_misconception"
    HISTORICAL_CONTEXT = "historical_context"
    COMPARATIVE_INSIGHT = "comparative_insight"
    TENSION_POINT = "tension_point"
    EDGE_CASE = "edge_case"


@dataclass
class SectionInsight:
    """Extracted insights from a document section."""

    section_number: int
    section_title: str
    section_text: str

    # Core analysis
    core_principle: str = ""  # Fundamental idea protected/established
    practical_meaning: str = ""  # How it affects daily life
    common_misconceptions: list[str] = field(default_factory=list)
    edge_cases: list[str] = field(default_factory=list)
    related_concepts: list[str] = field(default_factory=list)

    # Advanced analysis
    tensions: list[str] = field(default_factory=list)  # Competing values/concepts
    analogies: list[str] = field(default_factory=list)  # Relatable comparisons
    implications: list[str] = field(default_factory=list)  # Real-world implications
    historical_notes: list[str] = field(default_factory=list)

    # Metadata
    insight_quality_score: float = 0.0  # 0.0-1.0 rating
    keywords: list[str] = field(default_factory=list)

    def has_sufficient_depth(self) -> bool:
        """Check if insight has enough depth for synthesis."""
        has_core = bool(self.core_principle)
        has_practical = bool(self.practical_meaning)
        has_details = len(self.implications) > 0 or len(self.analogies) > 0
        return has_core and has_practical and has_details

    def to_prompt_context(self) -> str:
        """Format insight for prompt injection."""
        parts = [
            f"SECTION {self.section_number}: {self.section_title}",
            f"\nCORE PRINCIPLE: {self.core_principle}" if self.core_principle else "",
            f"\nPRACTICAL MEANING: {self.practical_meaning}" if self.practical_meaning else "",
        ]

        if self.common_misconceptions:
            parts.append(f"\nCOMMON MISCONCEPTIONS: {'; '.join(self.common_misconceptions)}")

        if self.tensions:
            parts.append(f"\nTENSIONS: {'; '.join(self.tensions)}")

        if self.analogies:
            parts.append(f"\nANALOGIES: {'; '.join(self.analogies)}")

        if self.implications:
            parts.append(f"\nIMPLICATIONS: {'; '.join(self.implications)}")

        return "".join(parts)


@dataclass
class InsightConnection:
    """A connection between two section insights."""

    source_section: int
    target_section: int
    connection_type: str  # "supports", "contrasts", "extends", "limits"
    description: str
    strength: float = 0.5  # 0.0-1.0


@dataclass
class AnalysisResult:
    """Result of section analysis."""

    insights: list[SectionInsight]
    connections: list[InsightConnection]
    overall_themes: list[str]
    synthesis_potential: float = 0.0  # How rich the material is for synthesis


class InsightAnalyzer:
    """Analyzes document sections to extract insights for synthesis."""

    # Keywords that suggest different insight types
    PRINCIPLE_KEYWORDS = [
        "right", "freedom", "protect", "guarantee", "ensure", "entitle",
        "shall", "must", "duty", "obligation", "prohibit", "forbid"
    ]

    APPLICATION_KEYWORDS = [
        "apply", "enforce", "implement", "exercise", "practice",
        "access", "use", "benefit", "claim", "seek"
    ]

    LIMITATION_KEYWORDS = [
        "limit", "restrict", "except", "unless", "subject to",
        "provided that", "in accordance with", "reasonable"
    ]

    TENSION_KEYWORDS = [
        "balance", "weigh", "consider", "competing", "conflicting",
        "reconcile", "versus", "against", "between"
    ]

    def __init__(self, llm_provider: Optional[object] = None):
        """Initialize the insight analyzer.

        Args:
            llm_provider: Optional LLM provider for deep analysis.
        """
        self._llm = llm_provider

    async def analyze_section(
        self,
        section: DocumentSection,
        use_llm: bool = True
    ) -> SectionInsight:
        """Analyze a single section for insights.

        Args:
            section: The document section to analyze.
            use_llm: Whether to use LLM for deeper analysis.

        Returns:
            SectionInsight with extracted information.
        """
        insight = SectionInsight(
            section_number=section.section_number,
            section_title=section.title or f"Section {section.section_number}",
            section_text=section.content
        )

        # Basic keyword-based analysis
        self._extract_keywords(insight)
        self._identify_principle_type(insight)
        self._identify_tensions(insight)
        self._generate_basic_analogies(insight)

        # LLM-powered deep analysis
        if use_llm and self._llm:
            await self._deep_analyze(insight)

        # Calculate quality score
        insight.insight_quality_score = self._calculate_quality_score(insight)

        return insight

    async def analyze_multiple_sections(
        self,
        sections: list[DocumentSection],
        use_llm: bool = True
    ) -> AnalysisResult:
        """Analyze multiple sections and find connections.

        Args:
            sections: List of document sections to analyze.
            use_llm: Whether to use LLM for deeper analysis.

        Returns:
            AnalysisResult with insights and connections.
        """
        insights = []
        for section in sections:
            insight = await self.analyze_section(section, use_llm)
            insights.append(insight)

        connections = self._find_connections(insights)
        themes = self._extract_themes(insights)
        synthesis_potential = self._calculate_synthesis_potential(insights, connections)

        return AnalysisResult(
            insights=insights,
            connections=connections,
            overall_themes=themes,
            synthesis_potential=synthesis_potential
        )

    def find_connections(
        self,
        insights: list[SectionInsight]
    ) -> list[InsightConnection]:
        """Find connections between section insights.

        Args:
            insights: List of section insights to connect.

        Returns:
            List of identified connections.
        """
        return self._find_connections(insights)

    def extract_implications(
        self,
        insight: SectionInsight
    ) -> list[str]:
        """Generate practical implications from an insight.

        Args:
            insight: The section insight to analyze.

        Returns:
            List of practical implications.
        """
        implications = []
        text_lower = insight.section_text.lower()

        # Rights implications
        if any(kw in text_lower for kw in ["right to", "entitled to", "freedom of"]):
            implications.append(
                f"Citizens can exercise this right in their daily interactions"
            )
            implications.append(
                f"Government must respect and protect this entitlement"
            )

        # Limitation implications
        if any(kw in text_lower for kw in self.LIMITATION_KEYWORDS):
            implications.append(
                f"This right has boundaries that must be understood"
            )
            implications.append(
                f"Context matters when applying this provision"
            )

        # Duty implications
        if "duty" in text_lower or "obligation" in text_lower:
            implications.append(
                f"There are responsibilities attached to this provision"
            )

        return implications

    def identify_tensions(
        self,
        insights: list[SectionInsight]
    ) -> list[tuple[SectionInsight, SectionInsight, str]]:
        """Identify tensions between different insights.

        Args:
            insights: List of insights to compare.

        Returns:
            List of tuples (insight1, insight2, tension_description).
        """
        tensions = []

        # Common tension pairs in constitutional context
        tension_pairs = [
            ("freedom", "security", "The classic balance between liberty and safety"),
            ("privacy", "transparency", "Individual privacy vs public accountability"),
            ("equality", "freedom", "Equal treatment vs freedom of choice"),
            ("property", "public interest", "Private ownership vs collective needs"),
            ("speech", "dignity", "Expression vs protection from harm"),
        ]

        for i, insight1 in enumerate(insights):
            for insight2 in insights[i + 1:]:
                text1_lower = insight1.section_text.lower()
                text2_lower = insight2.section_text.lower()

                for concept1, concept2, description in tension_pairs:
                    if concept1 in text1_lower and concept2 in text2_lower:
                        tensions.append((insight1, insight2, description))
                    elif concept2 in text1_lower and concept1 in text2_lower:
                        tensions.append((insight1, insight2, description))

        return tensions

    def _extract_keywords(self, insight: SectionInsight) -> None:
        """Extract relevant keywords from section text."""
        text_lower = insight.section_text.lower()
        keywords = []

        all_keywords = (
            self.PRINCIPLE_KEYWORDS +
            self.APPLICATION_KEYWORDS +
            self.LIMITATION_KEYWORDS
        )

        for keyword in all_keywords:
            if keyword in text_lower:
                keywords.append(keyword)

        insight.keywords = keywords

    def _identify_principle_type(self, insight: SectionInsight) -> None:
        """Identify the core principle from keywords."""
        text_lower = insight.section_text.lower()

        # Determine principle type
        if "right to" in text_lower:
            insight.core_principle = self._extract_right_statement(insight.section_text)
        elif "shall not" in text_lower or "prohibit" in text_lower:
            insight.core_principle = "Protection against specific government actions"
        elif "duty" in text_lower:
            insight.core_principle = "Establishes an obligation or responsibility"
        elif "freedom" in text_lower:
            insight.core_principle = self._extract_freedom_statement(insight.section_text)
        else:
            insight.core_principle = "Establishes a framework or procedure"

        # Generate practical meaning
        insight.practical_meaning = self._generate_practical_meaning(insight)

    def _extract_right_statement(self, text: str) -> str:
        """Extract a 'right to' statement from text."""
        import re
        match = re.search(r"right to\s+([^.,;]+)", text.lower())
        if match:
            return f"Guarantees the right to {match.group(1).strip()}"
        return "Establishes a protected right"

    def _extract_freedom_statement(self, text: str) -> str:
        """Extract a 'freedom of' statement from text."""
        import re
        match = re.search(r"freedom of\s+([^.,;]+)", text.lower())
        if match:
            return f"Protects freedom of {match.group(1).strip()}"
        return "Protects a fundamental freedom"

    def _generate_practical_meaning(self, insight: SectionInsight) -> str:
        """Generate practical meaning based on principle."""
        keywords = insight.keywords
        text_lower = insight.section_text.lower()

        if "access" in text_lower:
            return "Ensures people can obtain necessary services or information"
        elif "protect" in text_lower:
            return "Shields individuals from harm or interference"
        elif "equality" in text_lower or "equal" in text_lower:
            return "Ensures fair and equal treatment regardless of differences"
        elif "dignity" in text_lower:
            return "Requires respectful treatment of all persons"
        elif "property" in text_lower:
            return "Governs what people own and how they can use it"
        elif "vote" in text_lower or "election" in text_lower:
            return "Enables participation in democratic processes"
        elif "speech" in text_lower or "expression" in text_lower:
            return "Allows people to share ideas and opinions openly"
        else:
            return "Affects how citizens interact with government and each other"

    def _identify_tensions(self, insight: SectionInsight) -> None:
        """Identify tensions within a single section."""
        text_lower = insight.section_text.lower()
        tensions = []

        # Check for limitation language
        if "subject to" in text_lower:
            tensions.append("Right is qualified by reasonable limitations")
        if "except" in text_lower or "unless" in text_lower:
            tensions.append("Exceptions create boundaries around the right")
        if "balance" in text_lower:
            tensions.append("Multiple interests must be weighed")

        insight.tensions = tensions

    def _generate_basic_analogies(self, insight: SectionInsight) -> None:
        """Generate basic analogies for the insight."""
        text_lower = insight.section_text.lower()
        analogies = []

        # Common analogy patterns
        if "freedom of speech" in text_lower or "expression" in text_lower:
            analogies.append(
                "Like having a voice in a town square - you can speak, "
                "but not shout 'fire' in a crowded theater"
            )
        elif "privacy" in text_lower:
            analogies.append(
                "Like curtains on your windows - you choose what others see"
            )
        elif "property" in text_lower:
            analogies.append(
                "Like your home - it's yours, but you still can't ignore building codes"
            )
        elif "equality" in text_lower:
            analogies.append(
                "Like rules in a game - everyone plays by the same ones"
            )
        elif "dignity" in text_lower:
            analogies.append(
                "Like basic respect - something everyone deserves regardless of status"
            )
        elif "access" in text_lower:
            analogies.append(
                "Like a public library - open to all, not just the privileged few"
            )

        insight.analogies = analogies

    async def _deep_analyze(self, insight: SectionInsight) -> None:
        """Perform deep LLM-powered analysis."""
        if not self._llm:
            return

        # This will be implemented with actual LLM calls in integration
        # For now, enhance with pattern-based analysis
        self._enhance_misconceptions(insight)
        self._enhance_implications(insight)

    def _enhance_misconceptions(self, insight: SectionInsight) -> None:
        """Add common misconceptions based on the section type."""
        text_lower = insight.section_text.lower()
        misconceptions = []

        if "right" in text_lower:
            misconceptions.append(
                "Rights are not absolute - they can be limited in reasonable ways"
            )
        if "freedom" in text_lower:
            misconceptions.append(
                "Freedom doesn't mean freedom from consequences"
            )
        if "equality" in text_lower:
            misconceptions.append(
                "Equal treatment doesn't always mean identical treatment"
            )
        if "property" in text_lower:
            misconceptions.append(
                "Property rights don't override all other considerations"
            )

        insight.common_misconceptions = misconceptions

    def _enhance_implications(self, insight: SectionInsight) -> None:
        """Enhance practical implications."""
        implications = self.extract_implications(insight)
        insight.implications = implications

    def _find_connections(
        self,
        insights: list[SectionInsight]
    ) -> list[InsightConnection]:
        """Find connections between insights."""
        connections = []

        for i, insight1 in enumerate(insights):
            for j, insight2 in enumerate(insights[i + 1:], i + 1):
                # Check for keyword overlap
                common_keywords = set(insight1.keywords) & set(insight2.keywords)
                if common_keywords:
                    connections.append(InsightConnection(
                        source_section=insight1.section_number,
                        target_section=insight2.section_number,
                        connection_type="related",
                        description=f"Share concepts: {', '.join(common_keywords)}",
                        strength=min(len(common_keywords) / 3, 1.0)
                    ))

                # Check for complementary principles
                if self._are_complementary(insight1, insight2):
                    connections.append(InsightConnection(
                        source_section=insight1.section_number,
                        target_section=insight2.section_number,
                        connection_type="supports",
                        description="These provisions work together",
                        strength=0.7
                    ))

        return connections

    def _are_complementary(
        self,
        insight1: SectionInsight,
        insight2: SectionInsight
    ) -> bool:
        """Check if two insights are complementary."""
        # Simple heuristic: rights and their enforcement are complementary
        text1 = insight1.section_text.lower()
        text2 = insight2.section_text.lower()

        right_words = ["right", "freedom", "entitle"]
        enforce_words = ["enforce", "protect", "remedy", "court"]

        has_right1 = any(w in text1 for w in right_words)
        has_right2 = any(w in text2 for w in right_words)
        has_enforce1 = any(w in text1 for w in enforce_words)
        has_enforce2 = any(w in text2 for w in enforce_words)

        return (has_right1 and has_enforce2) or (has_right2 and has_enforce1)

    def _extract_themes(self, insights: list[SectionInsight]) -> list[str]:
        """Extract overall themes from multiple insights."""
        themes = []
        all_keywords = []

        for insight in insights:
            all_keywords.extend(insight.keywords)

        # Count keyword frequency
        keyword_counts = {}
        for kw in all_keywords:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

        # Top themes based on frequency
        sorted_keywords = sorted(
            keyword_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for keyword, count in sorted_keywords[:5]:
            if count > 1:
                themes.append(keyword.title())

        return themes

    def _calculate_quality_score(self, insight: SectionInsight) -> float:
        """Calculate insight quality score."""
        score = 0.0

        # Has core principle
        if insight.core_principle:
            score += 0.25

        # Has practical meaning
        if insight.practical_meaning:
            score += 0.25

        # Has analogies
        if insight.analogies:
            score += 0.2

        # Has implications
        if insight.implications:
            score += 0.15

        # Has misconceptions identified
        if insight.common_misconceptions:
            score += 0.15

        return min(score, 1.0)

    def _calculate_synthesis_potential(
        self,
        insights: list[SectionInsight],
        connections: list[InsightConnection]
    ) -> float:
        """Calculate how rich the material is for synthesis."""
        if not insights:
            return 0.0

        # Average quality score
        avg_quality = sum(i.insight_quality_score for i in insights) / len(insights)

        # Connection density (cap at 1.0)
        max_connections = len(insights) * (len(insights) - 1) / 2
        connection_density = min(len(connections) / max(max_connections, 1), 1.0)

        # Combine factors and cap result at 1.0
        return min((avg_quality * 0.6) + (connection_density * 0.4), 1.0)
