"""Content generation module."""

from contentmanager.core.content.formats import ContentFormatter
from contentmanager.core.content.generator import ContentGenerator
from contentmanager.core.content.templates import DEFAULT_DOCUMENT_CONTEXT, PromptTemplates
from contentmanager.core.content.validators import ContentValidator

# Synthesis system exports
from contentmanager.core.content.ai_pattern_filter import AIPatternFilter
from contentmanager.core.content.insight_analyzer import InsightAnalyzer, SectionInsight
from contentmanager.core.content.synthesis import SynthesisEngine, SynthesisMode
from contentmanager.core.content.scenarios import ScenarioGenerator
from contentmanager.core.content.persona_writer import PersonaWriter, WritingPersona
from contentmanager.core.content.prompt_variants import PromptVariants

__all__ = [
    # Core content classes
    "ContentGenerator",
    "ContentFormatter",
    "ContentValidator",
    "PromptTemplates",
    "DEFAULT_DOCUMENT_CONTEXT",
    # Synthesis system
    "AIPatternFilter",
    "InsightAnalyzer",
    "SectionInsight",
    "SynthesisEngine",
    "SynthesisMode",
    "ScenarioGenerator",
    "PersonaWriter",
    "WritingPersona",
    "PromptVariants",
]
