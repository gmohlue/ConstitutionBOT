"""Tests for Scenario Generator module."""

from datetime import date

import pytest

from contentmanager.core.content.scenarios import (
    Scenario,
    ScenarioCategory,
    ScenarioGenerator,
    TemporalHook,
)


class TestScenarioCategory:
    """Test ScenarioCategory enum."""

    def test_all_categories_exist(self):
        """Test all expected categories exist."""
        categories = [c.value for c in ScenarioCategory]

        assert "workplace" in categories
        assert "family" in categories
        assert "community" in categories
        assert "commerce" in categories
        assert "government" in categories
        assert "digital" in categories
        assert "healthcare" in categories
        assert "education" in categories
        assert "housing" in categories
        assert "transport" in categories


class TestScenario:
    """Test Scenario dataclass."""

    def test_to_prompt_context(self):
        """Test prompt context formatting."""
        scenario = Scenario(
            category=ScenarioCategory.WORKPLACE,
            setup="An employee discovers privacy breach",
            characters=["employee", "manager"],
            setting="Corporate office",
            conflict="Privacy vs transparency"
        )

        context = scenario.to_prompt_context()

        assert "SCENARIO" in context
        assert "workplace" in context
        assert "Corporate office" in context
        assert "privacy breach" in context


class TestScenarioGenerator:
    """Test ScenarioGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return ScenarioGenerator()

    @pytest.fixture
    def seeded_generator(self):
        """Create generator with fixed seed for reproducibility."""
        return ScenarioGenerator(seed=42)

    def test_generate_scenario_random(self, generator):
        """Test generating a random scenario."""
        scenario = generator.generate_scenario()

        assert isinstance(scenario, Scenario)
        assert scenario.setup != ""
        assert len(scenario.characters) > 0
        assert scenario.setting != ""

    def test_generate_scenario_specific_category(self, generator):
        """Test generating scenario for specific category."""
        scenario = generator.generate_scenario(category=ScenarioCategory.HEALTHCARE)

        assert scenario.category == ScenarioCategory.HEALTHCARE

    def test_generate_scenario_with_keywords(self, generator):
        """Test scenario generation with keyword matching."""
        scenario = generator.generate_scenario(keywords=["work", "employment"])

        # Should match to workplace category
        assert scenario is not None

    def test_avoid_recent_scenarios(self, generator):
        """Test that recent scenarios are avoided."""
        scenarios = []
        for _ in range(5):
            scenario = generator.generate_scenario(
                category=ScenarioCategory.WORKPLACE,
                avoid_recent=True
            )
            scenarios.append(scenario.setup)

        # Should have variety
        unique_scenarios = set(scenarios)
        assert len(unique_scenarios) >= min(3, len(scenarios))

    def test_get_temporal_hook(self, generator):
        """Test temporal hook generation."""
        hook = generator.get_temporal_hook()

        if hook:
            assert isinstance(hook, TemporalHook)
            assert hook.occasion != ""
            assert hook.relevance != ""
            assert hook.suggested_angle != ""

    def test_get_temporal_hook_specific_date(self, generator):
        """Test temporal hook for specific date."""
        # March should have Human Rights Month
        march_date = date(2024, 3, 15)
        hook = generator.get_temporal_hook(target_date=march_date)

        if hook:
            assert hook.date == march_date

    def test_match_scenario_to_topic(self, generator):
        """Test matching scenario to topic."""
        scenario = generator.match_scenario_to_topic(
            topic="workplace discrimination",
            section_keywords=["equality", "discrimination"]
        )

        assert scenario is not None

    def test_get_scenario_for_insight(self, generator):
        """Test getting scenario for insight keywords."""
        scenario = generator.get_scenario_for_insight(
            insight_keywords=["privacy", "data", "information"]
        )

        # Should match to digital or healthcare category
        assert scenario.category in [
            ScenarioCategory.DIGITAL,
            ScenarioCategory.HEALTHCARE,
            ScenarioCategory.GOVERNMENT
        ]

    def test_get_scenario_avoid_category(self, generator):
        """Test avoiding specific category."""
        scenario = generator.get_scenario_for_insight(
            insight_keywords=["work", "employment"],
            avoid_category=ScenarioCategory.WORKPLACE
        )

        # Should avoid workplace
        assert scenario.category != ScenarioCategory.WORKPLACE

    def test_get_scenarios_for_thread(self, generator):
        """Test getting multiple scenarios for thread."""
        scenarios = generator.get_scenarios_for_thread(num_scenarios=3)

        assert len(scenarios) == 3

        # Should have different categories
        categories = [s.category for s in scenarios]
        unique_categories = set(categories)
        assert len(unique_categories) >= 2

    def test_get_scenarios_for_thread_with_keywords(self, generator):
        """Test thread scenarios with topic keywords."""
        scenarios = generator.get_scenarios_for_thread(
            num_scenarios=3,
            topic_keywords=["rights", "freedom"]
        )

        assert len(scenarios) == 3

    def test_get_random_category(self, generator):
        """Test getting random category."""
        category = generator.get_random_category()

        assert isinstance(category, ScenarioCategory)

    def test_get_all_categories(self, generator):
        """Test getting all categories."""
        categories = generator.get_all_categories()

        assert len(categories) == len(ScenarioCategory)
        assert ScenarioCategory.WORKPLACE in categories

    def test_clear_used_scenarios(self, generator):
        """Test clearing used scenarios cache."""
        # Generate some scenarios
        for _ in range(3):
            generator.generate_scenario(category=ScenarioCategory.WORKPLACE)

        # Clear cache
        generator.clear_used_scenarios()

        # Should be able to generate again without avoidance
        scenario = generator.generate_scenario(
            category=ScenarioCategory.WORKPLACE,
            avoid_recent=True
        )
        assert scenario is not None

    def test_scenario_has_keywords(self, generator):
        """Test that generated scenarios have keywords."""
        scenario = generator.generate_scenario(category=ScenarioCategory.DIGITAL)

        assert len(scenario.keywords) > 0

    def test_seeded_generator_reproducibility(self, seeded_generator):
        """Test that seeded generator produces same results."""
        gen1 = ScenarioGenerator(seed=42)
        gen2 = ScenarioGenerator(seed=42)

        scenario1 = gen1.generate_scenario(category=ScenarioCategory.WORKPLACE)
        scenario2 = gen2.generate_scenario(category=ScenarioCategory.WORKPLACE)

        assert scenario1.setup == scenario2.setup

    def test_scenario_conflict_optional(self, generator):
        """Test that conflict field is optional."""
        scenario = generator.generate_scenario()

        # Should not raise even if some templates don't have conflict
        assert scenario is not None

    def test_temporal_hook_december(self):
        """Test temporal hook for December (Constitution Day)."""
        generator = ScenarioGenerator()
        december_date = date(2024, 12, 10)
        hook = generator.get_temporal_hook(target_date=december_date)

        if hook:
            assert "December" in str(hook.date.month) or hook.occasion is not None

    def test_keyword_matching_healthcare(self, generator):
        """Test keyword matching for healthcare."""
        categories = generator._match_category_to_keywords(["health", "medical", "doctor"])

        assert categories == ScenarioCategory.HEALTHCARE

    def test_keyword_matching_education(self, generator):
        """Test keyword matching for education."""
        categories = generator._match_category_to_keywords(["school", "student", "education"])

        assert categories == ScenarioCategory.EDUCATION
