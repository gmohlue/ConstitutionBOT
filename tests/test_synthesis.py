"""Tests for Synthesis Engine module."""

import pytest

from contentmanager.core.content.synthesis import (
    NarrativeFrame,
    SynthesisContext,
    SynthesisEngine,
    SynthesisMode,
    SynthesizedContent,
)
from contentmanager.core.content.insight_analyzer import SectionInsight


class TestSynthesisMode:
    """Test SynthesisMode enum."""

    def test_all_modes_exist(self):
        """Test all expected synthesis modes exist."""
        modes = [m.value for m in SynthesisMode]

        assert "explain" in modes
        assert "contrast" in modes
        assert "challenge" in modes
        assert "apply" in modes
        assert "story" in modes
        assert "myth_bust" in modes
        assert "implications" in modes


class TestSynthesisContext:
    """Test SynthesisContext dataclass."""

    @pytest.fixture
    def sample_insight(self):
        """Create a sample insight for testing."""
        return SectionInsight(
            section_number=9,
            section_title="Equality",
            section_text="Everyone has the right to equality.",
            core_principle="Equal treatment for all",
            practical_meaning="No discrimination in daily life",
            insight_quality_score=0.8
        )

    def test_get_primary_insight(self, sample_insight):
        """Test getting primary insight from context."""
        context = SynthesisContext(
            insights=[sample_insight],
            mode=SynthesisMode.EXPLAIN
        )

        primary = context.get_primary_insight()
        assert primary == sample_insight

    def test_get_primary_insight_empty(self):
        """Test getting primary insight with no insights."""
        context = SynthesisContext(
            insights=[],
            mode=SynthesisMode.EXPLAIN
        )

        assert context.get_primary_insight() is None

    def test_get_primary_insight_highest_quality(self):
        """Test that highest quality insight is returned."""
        insight1 = SectionInsight(
            section_number=1,
            section_title="Test1",
            section_text="Test",
            insight_quality_score=0.5
        )
        insight2 = SectionInsight(
            section_number=2,
            section_title="Test2",
            section_text="Test",
            insight_quality_score=0.9
        )

        context = SynthesisContext(
            insights=[insight1, insight2],
            mode=SynthesisMode.CHALLENGE
        )

        primary = context.get_primary_insight()
        assert primary.section_number == 2


class TestSynthesizedContent:
    """Test SynthesizedContent dataclass."""

    def test_full_content_from_parts(self):
        """Test full content generation from parts."""
        content = SynthesizedContent(
            raw_text="Raw content here",
            mode=SynthesisMode.EXPLAIN,
            hook="Here's the thing:",
            main_body="Rights matter in daily life.",
            closing="Think about it.",
        )

        full = content.full_content
        assert "Here's the thing:" in full
        assert "Rights matter" in full
        assert "Think about it" in full

    def test_full_content_fallback(self):
        """Test full content falls back to raw text."""
        content = SynthesizedContent(
            raw_text="Just raw text",
            mode=SynthesisMode.CHALLENGE,
        )

        assert content.full_content == "Just raw text"


class TestSynthesisEngine:
    """Test SynthesisEngine class."""

    @pytest.fixture
    def engine(self):
        """Create engine instance."""
        return SynthesisEngine()

    @pytest.fixture
    def sample_insight(self):
        """Create a sample insight."""
        return SectionInsight(
            section_number=16,
            section_title="Freedom of expression",
            section_text="Everyone has the right to freedom of expression.",
            core_principle="People can speak their minds",
            practical_meaning="You can share your opinions",
            common_misconceptions=["Speech has no limits"],
            tensions=["Free speech vs hate speech"],
            analogies=["Like having a voice in a town square"],
            implications=["Citizens can criticize government"],
            insight_quality_score=0.8
        )

    @pytest.fixture
    def sample_context(self, sample_insight):
        """Create a sample synthesis context."""
        return SynthesisContext(
            insights=[sample_insight],
            mode=SynthesisMode.EXPLAIN,
            scenario_category="community"
        )

    @pytest.mark.asyncio
    async def test_synthesize_explain(self, engine, sample_context):
        """Test explain synthesis mode."""
        sample_context.mode = SynthesisMode.EXPLAIN
        result = await engine.synthesize(sample_context)

        assert isinstance(result, SynthesizedContent)
        assert result.mode == SynthesisMode.EXPLAIN
        assert result.raw_text != ""

    @pytest.mark.asyncio
    async def test_synthesize_contrast(self, engine, sample_context):
        """Test contrast synthesis mode."""
        sample_context.mode = SynthesisMode.CONTRAST
        result = await engine.synthesize(sample_context)

        assert result.mode == SynthesisMode.CONTRAST

    @pytest.mark.asyncio
    async def test_synthesize_challenge(self, engine, sample_context):
        """Test challenge synthesis mode."""
        sample_context.mode = SynthesisMode.CHALLENGE
        result = await engine.synthesize(sample_context)

        assert result.mode == SynthesisMode.CHALLENGE

    @pytest.mark.asyncio
    async def test_synthesize_apply(self, engine, sample_context):
        """Test apply synthesis mode."""
        sample_context.mode = SynthesisMode.APPLY
        result = await engine.synthesize(sample_context)

        assert result.mode == SynthesisMode.APPLY

    @pytest.mark.asyncio
    async def test_synthesize_story(self, engine, sample_context):
        """Test story synthesis mode."""
        sample_context.mode = SynthesisMode.STORY
        result = await engine.synthesize(sample_context)

        assert result.mode == SynthesisMode.STORY

    @pytest.mark.asyncio
    async def test_synthesize_myth_bust(self, engine, sample_context):
        """Test myth bust synthesis mode."""
        sample_context.mode = SynthesisMode.MYTH_BUST
        result = await engine.synthesize(sample_context)

        assert result.mode == SynthesisMode.MYTH_BUST

    @pytest.mark.asyncio
    async def test_synthesize_implications(self, engine, sample_context):
        """Test implications synthesis mode."""
        sample_context.mode = SynthesisMode.IMPLICATIONS
        result = await engine.synthesize(sample_context)

        assert result.mode == SynthesisMode.IMPLICATIONS

    @pytest.mark.asyncio
    async def test_synthesize_no_insights(self, engine):
        """Test synthesis with no insights."""
        context = SynthesisContext(
            insights=[],
            mode=SynthesisMode.EXPLAIN
        )

        result = await engine.synthesize(context)
        assert "Insufficient" in result.raw_text

    def test_generate_hook(self, engine, sample_insight):
        """Test hook generation."""
        hook = engine.generate_hook(sample_insight, SynthesisMode.EXPLAIN)

        assert hook != ""
        assert isinstance(hook, str)

    def test_generate_hook_different_modes(self, engine, sample_insight):
        """Test hook generation for different modes."""
        modes = list(SynthesisMode)
        hooks = set()

        for mode in modes:
            hook = engine.generate_hook(sample_insight, mode)
            hooks.add(hook)

        # Should generate different hooks for different modes
        assert len(hooks) > 1

    def test_create_narrative_frame(self, engine, sample_insight):
        """Test narrative frame creation."""
        frame = engine.create_narrative_frame(sample_insight)

        assert isinstance(frame, NarrativeFrame)
        assert frame.setup != ""
        assert frame.tension != ""
        assert frame.insight != ""
        assert frame.resolution != ""

    def test_narrative_frame_to_narrative(self, engine, sample_insight):
        """Test narrative conversion."""
        frame = engine.create_narrative_frame(sample_insight)
        narrative = frame.to_narrative()

        assert isinstance(narrative, str)
        assert len(narrative) > 0

    def test_build_argument(self, engine, sample_insight):
        """Test argument structure building."""
        argument = engine.build_argument(sample_insight)

        assert "thesis" in argument
        assert "evidence" in argument
        assert "conclusion" in argument

    def test_build_argument_custom_thesis(self, engine, sample_insight):
        """Test argument building with custom thesis."""
        custom_thesis = "Freedom of expression is essential"
        argument = engine.build_argument(sample_insight, thesis=custom_thesis)

        assert argument["thesis"] == custom_thesis

    def test_synthesize_perspective(self, engine, sample_insight):
        """Test perspective synthesis."""
        result = engine.synthesize_perspective(
            sample_insight,
            SynthesisMode.CHALLENGE
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_synthesis_score_calculation(self, engine, sample_context):
        """Test synthesis quality score is calculated."""
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            engine.synthesize(sample_context)
        )

        assert 0.0 <= result.synthesis_score <= 1.0

    def test_source_sections_tracked(self, engine, sample_context):
        """Test that source sections are tracked."""
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            engine.synthesize(sample_context)
        )

        assert len(result.source_sections) > 0
        assert 16 in result.source_sections


class TestNarrativeFrame:
    """Test NarrativeFrame dataclass."""

    def test_to_narrative(self):
        """Test narrative conversion."""
        frame = NarrativeFrame(
            setup="Picture this scenario.",
            tension="But then something changes.",
            insight="The realization comes.",
            resolution="Now things are different."
        )

        narrative = frame.to_narrative()
        assert "Picture this" in narrative
        assert "changes" in narrative
        assert "realization" in narrative
        assert "different" in narrative
