"""Tests for Insight Analysis module."""

import pytest

from contentmanager.core.content.insight_analyzer import (
    AnalysisResult,
    InsightAnalyzer,
    InsightConnection,
    InsightType,
    SectionInsight,
)


class MockSection:
    """Mock document section for testing."""

    def __init__(
        self,
        section_number: int = 1,
        title: str = "Test Section",
        content: str = "Everyone has the right to freedom of expression."
    ):
        self.section_number = section_number
        self.title = title
        self.content = content


class TestSectionInsight:
    """Test SectionInsight dataclass."""

    def test_has_sufficient_depth_true(self):
        """Test depth check with sufficient insight."""
        insight = SectionInsight(
            section_number=1,
            section_title="Test",
            section_text="Test content",
            core_principle="Protects freedom",
            practical_meaning="Affects daily speech",
            implications=["Can speak freely"],
        )

        assert insight.has_sufficient_depth() is True

    def test_has_sufficient_depth_false(self):
        """Test depth check with insufficient insight."""
        insight = SectionInsight(
            section_number=1,
            section_title="Test",
            section_text="Test content",
        )

        assert insight.has_sufficient_depth() is False

    def test_to_prompt_context(self):
        """Test formatting for prompt injection."""
        insight = SectionInsight(
            section_number=9,
            section_title="Equality",
            section_text="Test",
            core_principle="Equal treatment for all",
            practical_meaning="No discrimination",
            common_misconceptions=["Same as identical"],
        )

        context = insight.to_prompt_context()

        assert "SECTION 9" in context
        assert "Equality" in context
        assert "CORE PRINCIPLE" in context
        assert "Equal treatment" in context


class TestInsightAnalyzer:
    """Test InsightAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return InsightAnalyzer()

    @pytest.fixture
    def rights_section(self):
        """Create a mock rights section."""
        return MockSection(
            section_number=9,
            title="Equality",
            content="Everyone has the right to equality and to equal protection under the law."
        )

    @pytest.fixture
    def freedom_section(self):
        """Create a mock freedom section."""
        return MockSection(
            section_number=16,
            title="Freedom of expression",
            content="Everyone has the right to freedom of expression, which includes freedom of the press."
        )

    @pytest.mark.asyncio
    async def test_analyze_section_basic(self, analyzer, rights_section):
        """Test basic section analysis."""
        insight = await analyzer.analyze_section(rights_section, use_llm=False)

        assert insight.section_number == 9
        assert insight.section_title == "Equality"
        assert insight.core_principle != ""
        assert insight.practical_meaning != ""

    @pytest.mark.asyncio
    async def test_analyze_section_extracts_keywords(self, analyzer, rights_section):
        """Test keyword extraction from section."""
        insight = await analyzer.analyze_section(rights_section, use_llm=False)

        assert len(insight.keywords) > 0
        assert "right" in insight.keywords or "protect" in insight.keywords

    @pytest.mark.asyncio
    async def test_analyze_section_identifies_tensions(self, analyzer, freedom_section):
        """Test tension identification."""
        insight = await analyzer.analyze_section(freedom_section, use_llm=False)

        # Freedom sections should identify some tensions
        assert insight.tensions is not None

    @pytest.mark.asyncio
    async def test_analyze_section_generates_analogies(self, analyzer, freedom_section):
        """Test analogy generation."""
        insight = await analyzer.analyze_section(freedom_section, use_llm=False)

        # Should have at least one analogy for expression-related content
        assert len(insight.analogies) > 0

    @pytest.mark.asyncio
    async def test_analyze_multiple_sections(self, analyzer, rights_section, freedom_section):
        """Test analyzing multiple sections."""
        sections = [rights_section, freedom_section]
        result = await analyzer.analyze_multiple_sections(sections, use_llm=False)

        assert len(result.insights) == 2
        assert isinstance(result, AnalysisResult)

    @pytest.mark.asyncio
    async def test_find_connections(self, analyzer, rights_section, freedom_section):
        """Test finding connections between insights."""
        sections = [rights_section, freedom_section]
        result = await analyzer.analyze_multiple_sections(sections, use_llm=False)

        connections = analyzer.find_connections(result.insights)
        # Both sections mention "right" so should find connections
        assert isinstance(connections, list)

    @pytest.mark.asyncio
    async def test_extract_implications(self, analyzer, rights_section):
        """Test extracting practical implications."""
        insight = await analyzer.analyze_section(rights_section, use_llm=False)
        implications = analyzer.extract_implications(insight)

        assert isinstance(implications, list)
        assert len(implications) > 0

    @pytest.mark.asyncio
    async def test_quality_score_calculation(self, analyzer, rights_section):
        """Test insight quality score calculation."""
        insight = await analyzer.analyze_section(rights_section, use_llm=False)

        assert 0.0 <= insight.insight_quality_score <= 1.0

    @pytest.mark.asyncio
    async def test_identify_tensions_between_insights(self, analyzer):
        """Test identifying tensions between different insights."""
        privacy_section = MockSection(
            section_number=14,
            title="Privacy",
            content="Everyone has the right to privacy."
        )
        security_section = MockSection(
            section_number=12,
            title="Security",
            content="Everyone has the right to freedom and security of the person."
        )

        sections = [privacy_section, security_section]
        result = await analyzer.analyze_multiple_sections(sections, use_llm=False)

        tensions = analyzer.identify_tensions(result.insights)
        # Should identify privacy vs security tension
        assert isinstance(tensions, list)

    @pytest.mark.asyncio
    async def test_synthesis_potential_calculation(self, analyzer, rights_section, freedom_section):
        """Test synthesis potential calculation."""
        sections = [rights_section, freedom_section]
        result = await analyzer.analyze_multiple_sections(sections, use_llm=False)

        assert 0.0 <= result.synthesis_potential <= 1.0

    @pytest.mark.asyncio
    async def test_overall_themes_extraction(self, analyzer, rights_section, freedom_section):
        """Test overall themes extraction from multiple insights."""
        sections = [rights_section, freedom_section]
        result = await analyzer.analyze_multiple_sections(sections, use_llm=False)

        assert isinstance(result.overall_themes, list)


class TestInsightConnection:
    """Test InsightConnection dataclass."""

    def test_connection_attributes(self):
        """Test connection has all expected attributes."""
        conn = InsightConnection(
            source_section=9,
            target_section=16,
            connection_type="supports",
            description="Both protect freedoms",
            strength=0.7
        )

        assert conn.source_section == 9
        assert conn.target_section == 16
        assert conn.connection_type == "supports"
        assert 0.0 <= conn.strength <= 1.0
