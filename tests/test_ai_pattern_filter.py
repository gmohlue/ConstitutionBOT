"""Tests for AI Pattern Detection and Filtering module."""

import pytest

from contentmanager.core.content.ai_pattern_filter import (
    AIPatternFilter,
    AIPatternReport,
    DetectedPattern,
    PatternCategory,
)


class TestAIPatternFilter:
    """Test AIPatternFilter class."""

    @pytest.fixture
    def filter(self):
        """Create a filter instance."""
        return AIPatternFilter()

    @pytest.fixture
    def strict_filter(self):
        """Create a strict mode filter instance."""
        return AIPatternFilter(strict_mode=True)

    def test_detect_cliche_openers(self, filter):
        """Test detection of cliche opening phrases."""
        content = "It's important to note that the Constitution protects rights."
        report = filter.analyze(content)

        assert len(report.patterns) > 0
        opener_patterns = [
            p for p in report.patterns
            if p.category == PatternCategory.CLICHE_OPENER
        ]
        assert len(opener_patterns) > 0

    def test_detect_corporate_speak(self, filter):
        """Test detection of corporate buzzwords."""
        content = "We need to leverage the Constitution to empower citizens robustly."
        report = filter.analyze(content)

        corporate_patterns = [
            p for p in report.patterns
            if p.category == PatternCategory.CORPORATE_SPEAK
        ]
        assert len(corporate_patterns) >= 2  # leverage, empower, robustly

    def test_detect_cliche_phrases(self, filter):
        """Test detection of cliche phrases."""
        content = "At the end of the day, rights play a crucial role in society."
        report = filter.analyze(content)

        cliche_patterns = [
            p for p in report.patterns
            if p.category == PatternCategory.CLICHE_PHRASE
        ]
        assert len(cliche_patterns) >= 1

    def test_detect_hedging(self, filter):
        """Test detection of excessive hedging."""
        content = "Perhaps it could be said that maybe this might potentially be important."
        report = filter.analyze(content)

        hedging_patterns = [
            p for p in report.patterns
            if p.category == PatternCategory.HEDGING
        ]
        assert len(hedging_patterns) >= 1

    def test_detect_list_structures(self, filter):
        """Test detection of AI-typical list structures."""
        content = "First, we discuss rights. Second, we cover duties. Third, we examine enforcement."
        report = filter.analyze(content)

        list_patterns = [
            p for p in report.patterns
            if p.category == PatternCategory.LIST_STRUCTURE
        ]
        assert len(list_patterns) >= 1

    def test_ai_score_clean_content(self, filter):
        """Test that clean content gets low AI score."""
        content = "Rights matter. They protect us daily. Think about your morning commute."
        report = filter.analyze(content)

        assert report.ai_score < 0.5

    def test_ai_score_ai_content(self, filter):
        """Test that AI-typical content gets higher score."""
        content = (
            "It's important to note that in today's world, "
            "we must leverage robust solutions to empower citizens. "
            "First, let's delve into the implications."
        )
        report = filter.analyze(content)

        assert report.ai_score > 0.3

    def test_sentence_variance_uniform(self, filter):
        """Test low variance with uniform sentences."""
        content = "This is five words. That is five words. Here are five words."
        report = filter.analyze(content)

        assert report.sentence_variance < 0.5

    def test_sentence_variance_varied(self, filter):
        """Test high variance with varied sentences."""
        content = "Short. This sentence is much longer and has more variation in it. Another short one."
        report = filter.analyze(content)

        assert report.sentence_variance > 0.3

    def test_humanize_removes_cliches(self, filter):
        """Test that humanize removes cliche openers."""
        content = "It's important to note that rights exist."
        humanized = filter.humanize(content)

        assert "It's important to note" not in humanized

    def test_humanize_replaces_buzzwords(self, filter):
        """Test that humanize replaces corporate buzzwords."""
        content = "We must leverage these tools to utilize our resources."
        humanized = filter.humanize(content)

        assert "leverage" not in humanized
        assert "utilize" not in humanized
        assert "use" in humanized

    def test_humanize_adds_contractions(self, filter):
        """Test that humanize adds contractions."""
        content = "It is true that they are correct and we are here."
        humanized = filter.humanize(content)

        assert "it's" in humanized.lower() or "they're" in humanized.lower()

    def test_validate_human_likeness_pass(self, filter):
        """Test validation passes for human-like content."""
        content = "There's something interesting about how we think about rights."
        is_valid, report = filter.validate_human_likeness(content, threshold=0.5)

        assert is_valid is True

    def test_validate_human_likeness_fail(self, filter):
        """Test validation fails for AI-like content."""
        content = (
            "It's important to note that we must delve into "
            "this robust framework to leverage synergies."
        )
        is_valid, report = filter.validate_human_likeness(content, threshold=0.3)

        assert is_valid is False

    def test_get_random_human_starter(self, filter):
        """Test getting random human starters."""
        starter = filter.get_random_human_starter()

        assert starter in filter.HUMAN_STARTERS

    def test_suggestions_generation(self, filter):
        """Test that suggestions are generated for problematic content."""
        content = "It's important to note that. First, Second, Third."
        report = filter.analyze(content)

        assert len(report.suggestions) > 0

    def test_strict_mode_detects_fillers(self, strict_filter):
        """Test strict mode detects filler words."""
        content = "This is basically essentially just very important."
        report = strict_filter.analyze(content)

        filler_patterns = [
            p for p in report.patterns
            if p.category == PatternCategory.FILLER_WORDS
        ]
        assert len(filler_patterns) >= 1

    def test_empty_content(self, filter):
        """Test handling of empty content."""
        report = filter.analyze("")

        assert report.ai_score == 0.0
        assert len(report.patterns) == 0

    def test_pattern_has_position(self, filter):
        """Test that detected patterns have position info."""
        content = "It's important to note that this matters."
        report = filter.analyze(content)

        for pattern in report.patterns:
            assert pattern.position is not None
            assert pattern.position[0] >= 0
            assert pattern.position[1] > pattern.position[0]

    def test_is_human_like_property(self, filter):
        """Test is_human_like property on report."""
        clean_content = "Simple and direct. That's how we communicate."
        report = filter.analyze(clean_content)

        assert report.is_human_like is True

    def test_pattern_count_property(self, filter):
        """Test pattern_count property on report."""
        content = "Leverage synergy to empower stakeholders robustly."
        report = filter.analyze(content)

        assert report.pattern_count == len(report.patterns)
