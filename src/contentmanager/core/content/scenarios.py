"""Scenario Generator Module.

This module generates relatable real-world scenarios for content synthesis
without requiring external APIs.
"""

import random
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class ScenarioCategory(Enum):
    """Categories of relatable scenarios."""

    WORKPLACE = "workplace"
    FAMILY = "family"
    COMMUNITY = "community"
    COMMERCE = "commerce"
    GOVERNMENT = "government"
    DIGITAL = "digital"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    HOUSING = "housing"
    TRANSPORT = "transport"


@dataclass
class Scenario:
    """A relatable real-world scenario."""

    category: ScenarioCategory
    setup: str  # The situation description
    characters: list[str]  # People involved
    setting: str  # Where it happens
    conflict: Optional[str] = None  # The tension or issue
    keywords: list[str] = field(default_factory=list)  # Related topic keywords
    temporal_context: Optional[str] = None  # Time-related context

    def to_prompt_context(self) -> str:
        """Format scenario for prompt injection."""
        parts = [
            f"SCENARIO ({self.category.value}):",
            f"Setting: {self.setting}",
            f"Situation: {self.setup}",
        ]
        if self.conflict:
            parts.append(f"Issue: {self.conflict}")
        return "\n".join(parts)


@dataclass
class TemporalHook:
    """A time-aware contextual hook."""

    date: date
    occasion: str
    relevance: str
    suggested_angle: str


class ScenarioGenerator:
    """Generates relatable real-world scenarios for content synthesis."""

    # Scenario templates by category
    SCENARIO_TEMPLATES = {
        ScenarioCategory.WORKPLACE: [
            {
                "setup": "An employee discovers their performance review was shared with colleagues without consent",
                "characters": ["employee", "manager", "HR representative"],
                "setting": "Corporate office",
                "conflict": "Privacy breach vs workplace transparency",
                "keywords": ["privacy", "dignity", "information", "employment"],
            },
            {
                "setup": "A worker is asked to work overtime without additional pay during a critical project",
                "characters": ["worker", "supervisor", "team lead"],
                "setting": "Small business",
                "conflict": "Labor rights vs business demands",
                "keywords": ["labor", "fair", "conditions", "work"],
            },
            {
                "setup": "An employee is denied a promotion after revealing their political views on social media",
                "characters": ["employee", "hiring committee", "colleague"],
                "setting": "Marketing firm",
                "conflict": "Free expression vs professional consequences",
                "keywords": ["expression", "speech", "freedom", "belief"],
            },
            {
                "setup": "A pregnant employee is subtly encouraged to take 'extended leave' indefinitely",
                "characters": ["pregnant employee", "manager", "coworker"],
                "setting": "Tech startup",
                "conflict": "Equality vs implicit discrimination",
                "keywords": ["equality", "discrimination", "gender", "unfair"],
            },
        ],
        ScenarioCategory.FAMILY: [
            {
                "setup": "Grandparents are denied visitation rights after their child's divorce",
                "characters": ["grandparents", "parent", "grandchild"],
                "setting": "Family home",
                "conflict": "Family bonds vs parental authority",
                "keywords": ["family", "children", "care", "rights"],
            },
            {
                "setup": "A teenager wants to make their own medical decisions against parents' wishes",
                "characters": ["teenager", "parents", "doctor"],
                "setting": "Hospital",
                "conflict": "Minor autonomy vs parental responsibility",
                "keywords": ["children", "health", "decision", "consent"],
            },
            {
                "setup": "An elderly parent's children disagree about care arrangements",
                "characters": ["elderly parent", "adult children", "caregiver"],
                "setting": "Family meeting",
                "conflict": "Dignity vs safety concerns",
                "keywords": ["dignity", "care", "elderly", "decision"],
            },
        ],
        ScenarioCategory.COMMUNITY: [
            {
                "setup": "Residents protest a new development that would demolish a historic neighborhood",
                "characters": ["residents", "developer", "city council"],
                "setting": "Community hall meeting",
                "conflict": "Property development vs community heritage",
                "keywords": ["property", "community", "culture", "heritage"],
            },
            {
                "setup": "A neighborhood watch group starts monitoring 'suspicious' newcomers",
                "characters": ["long-time resident", "new family", "watch coordinator"],
                "setting": "Suburban neighborhood",
                "conflict": "Security vs discrimination",
                "keywords": ["equality", "dignity", "freedom", "movement"],
            },
            {
                "setup": "Local religious groups clash over the use of shared community space",
                "characters": ["religious leaders", "community members", "space manager"],
                "setting": "Community center",
                "conflict": "Religious freedom vs equal access",
                "keywords": ["religion", "belief", "equality", "freedom"],
            },
        ],
        ScenarioCategory.COMMERCE: [
            {
                "setup": "A shop owner refuses service based on the customer's appearance",
                "characters": ["customer", "shop owner", "other patrons"],
                "setting": "Retail store",
                "conflict": "Business rights vs discrimination",
                "keywords": ["equality", "dignity", "discrimination", "public"],
            },
            {
                "setup": "A company's terms of service allow them to use customer data for AI training",
                "characters": ["consumer", "company", "data analyst"],
                "setting": "Online platform",
                "conflict": "Business innovation vs privacy",
                "keywords": ["privacy", "information", "consent", "data"],
            },
            {
                "setup": "A landlord increases rent by 50% in an area with limited housing options",
                "characters": ["tenant", "landlord", "housing advocate"],
                "setting": "Apartment complex",
                "conflict": "Property rights vs housing access",
                "keywords": ["housing", "property", "access", "shelter"],
            },
        ],
        ScenarioCategory.GOVERNMENT: [
            {
                "setup": "A permit application is delayed indefinitely without explanation",
                "characters": ["applicant", "government official", "supervisor"],
                "setting": "Municipal office",
                "conflict": "Administrative discretion vs accountability",
                "keywords": ["administrative", "justice", "fair", "procedure"],
            },
            {
                "setup": "Police conduct a search without a warrant citing 'reasonable suspicion'",
                "characters": ["citizen", "police officers", "lawyer"],
                "setting": "Public street",
                "conflict": "Security measures vs privacy rights",
                "keywords": ["privacy", "security", "search", "liberty"],
            },
            {
                "setup": "A journalist is denied access to public records about government spending",
                "characters": ["journalist", "government spokesperson", "editor"],
                "setting": "Government building",
                "conflict": "Transparency vs state interests",
                "keywords": ["information", "access", "press", "freedom"],
            },
        ],
        ScenarioCategory.DIGITAL: [
            {
                "setup": "A social media platform permanently bans a user for 'misinformation'",
                "characters": ["user", "platform moderator", "appeal reviewer"],
                "setting": "Online platform",
                "conflict": "Platform rules vs speech rights",
                "keywords": ["expression", "speech", "freedom", "media"],
            },
            {
                "setup": "An employer monitors all employee communications including personal messages",
                "characters": ["employee", "IT admin", "HR"],
                "setting": "Remote work",
                "conflict": "Workplace oversight vs privacy",
                "keywords": ["privacy", "communication", "surveillance", "work"],
            },
            {
                "setup": "A government proposes ID verification for all social media accounts",
                "characters": ["citizen", "lawmaker", "privacy advocate"],
                "setting": "Public debate",
                "conflict": "Accountability vs anonymity",
                "keywords": ["privacy", "identity", "freedom", "expression"],
            },
        ],
        ScenarioCategory.HEALTHCARE: [
            {
                "setup": "A patient is denied treatment because they can't prove insurance coverage",
                "characters": ["patient", "hospital administrator", "doctor"],
                "setting": "Emergency room",
                "conflict": "Healthcare access vs financial policies",
                "keywords": ["health", "access", "care", "life"],
            },
            {
                "setup": "Medical records are shared with a patient's employer without explicit consent",
                "characters": ["patient", "doctor", "employer"],
                "setting": "Medical office",
                "conflict": "Medical transparency vs privacy",
                "keywords": ["privacy", "health", "information", "confidential"],
            },
            {
                "setup": "A patient seeks an experimental treatment that doctors advise against",
                "characters": ["patient", "doctor", "family member"],
                "setting": "Hospital consultation room",
                "conflict": "Patient autonomy vs medical judgment",
                "keywords": ["health", "choice", "life", "decision"],
            },
        ],
        ScenarioCategory.EDUCATION: [
            {
                "setup": "A student is disciplined for wearing cultural clothing to school",
                "characters": ["student", "principal", "parent"],
                "setting": "Public school",
                "conflict": "Dress code vs cultural expression",
                "keywords": ["culture", "expression", "education", "religion"],
            },
            {
                "setup": "A university requires students to use specific pronouns in class discussions",
                "characters": ["student", "professor", "classmate"],
                "setting": "University classroom",
                "conflict": "Inclusion policies vs personal beliefs",
                "keywords": ["expression", "dignity", "belief", "equality"],
            },
            {
                "setup": "School assigns children to classes based on standardized test scores",
                "characters": ["student", "teacher", "parent"],
                "setting": "Elementary school",
                "conflict": "Educational efficiency vs equal opportunity",
                "keywords": ["education", "equality", "children", "opportunity"],
            },
        ],
        ScenarioCategory.HOUSING: [
            {
                "setup": "A family faces eviction during winter despite paying partial rent",
                "characters": ["tenant family", "landlord", "social worker"],
                "setting": "Rental apartment",
                "conflict": "Property rights vs shelter needs",
                "keywords": ["housing", "shelter", "property", "children"],
            },
            {
                "setup": "Rental applications are rejected based on applicants' country of origin",
                "characters": ["applicants", "property manager", "real estate agent"],
                "setting": "Housing market",
                "conflict": "Landlord choice vs discrimination",
                "keywords": ["equality", "discrimination", "housing", "nationality"],
            },
            {
                "setup": "A homeowner is forced to sell for a highway project at below-market value",
                "characters": ["homeowner", "government official", "real estate appraiser"],
                "setting": "Family home",
                "conflict": "Public infrastructure vs property rights",
                "keywords": ["property", "compensation", "government", "fair"],
            },
        ],
        ScenarioCategory.TRANSPORT: [
            {
                "setup": "A person with a disability is denied boarding due to 'safety concerns'",
                "characters": ["passenger", "transport staff", "supervisor"],
                "setting": "Public transit",
                "conflict": "Safety policies vs equal access",
                "keywords": ["equality", "dignity", "access", "disability"],
            },
            {
                "setup": "Ride-sharing app surcharges certain neighborhoods based on 'risk factors'",
                "characters": ["rider", "driver", "app company"],
                "setting": "Urban area",
                "conflict": "Business pricing vs discrimination",
                "keywords": ["equality", "movement", "discrimination", "service"],
            },
        ],
    }

    # Temporal occasions with constitutional relevance
    TEMPORAL_OCCASIONS = {
        # Monthly occasions
        1: [  # January
            {"occasion": "New Year", "relevance": "Fresh start, new resolutions for civic engagement",
             "angle": "What constitutional principles should guide our year?"},
        ],
        2: [  # February
            {"occasion": "Valentine's Day period", "relevance": "Love, relationships, family rights",
             "angle": "How does the constitution protect our loved ones?"},
        ],
        3: [  # March
            {"occasion": "Human Rights Month", "relevance": "Rights awareness",
             "angle": "Reflecting on rights we take for granted"},
            {"occasion": "Freedom Day (21st)", "relevance": "Democratic milestone",
             "angle": "How far we've come, how far to go"},
        ],
        4: [  # April
            {"occasion": "Freedom Month", "relevance": "April 27 elections anniversary",
             "angle": "The vote that changed everything"},
        ],
        5: [  # May
            {"occasion": "Workers' Month", "relevance": "Labor rights",
             "angle": "Constitutional protections at work"},
            {"occasion": "Africa Month", "relevance": "Continental identity",
             "angle": "African constitutionalism and SA's role"},
        ],
        6: [  # June
            {"occasion": "Youth Month", "relevance": "Youth Day (16th)",
             "angle": "Young people and constitutional awareness"},
        ],
        7: [  # July
            {"occasion": "Mandela Month", "relevance": "Legacy of constitutional democracy",
             "angle": "The constitutional vision Mandela helped build"},
        ],
        8: [  # August
            {"occasion": "Women's Month", "relevance": "Gender equality",
             "angle": "Constitutional protections for women"},
        ],
        9: [  # September
            {"occasion": "Heritage Month", "relevance": "Cultural rights",
             "angle": "Protecting diverse traditions under one constitution"},
        ],
        10: [  # October
            {"occasion": "Transport Month", "relevance": "Freedom of movement",
             "angle": "The right to move freely"},
        ],
        11: [  # November
            {"occasion": "Remembrance period", "relevance": "Honoring those who fought for rights",
             "angle": "Constitutional rights earned through struggle"},
        ],
        12: [  # December
            {"occasion": "Reconciliation Day (16th)", "relevance": "National unity",
             "angle": "The constitution as a reconciliation document"},
            {"occasion": "Constitution Day (10th)", "relevance": "Direct constitutional celebration",
             "angle": "Celebrating the supreme law of the land"},
        ],
    }

    # Keywords to category mapping for matching
    KEYWORD_CATEGORIES = {
        "work": [ScenarioCategory.WORKPLACE],
        "employment": [ScenarioCategory.WORKPLACE],
        "job": [ScenarioCategory.WORKPLACE],
        "labor": [ScenarioCategory.WORKPLACE],
        "family": [ScenarioCategory.FAMILY],
        "children": [ScenarioCategory.FAMILY, ScenarioCategory.EDUCATION],
        "parent": [ScenarioCategory.FAMILY],
        "marriage": [ScenarioCategory.FAMILY],
        "community": [ScenarioCategory.COMMUNITY],
        "neighborhood": [ScenarioCategory.COMMUNITY],
        "local": [ScenarioCategory.COMMUNITY],
        "business": [ScenarioCategory.COMMERCE],
        "consumer": [ScenarioCategory.COMMERCE],
        "shop": [ScenarioCategory.COMMERCE],
        "buy": [ScenarioCategory.COMMERCE],
        "sell": [ScenarioCategory.COMMERCE],
        "government": [ScenarioCategory.GOVERNMENT],
        "state": [ScenarioCategory.GOVERNMENT],
        "official": [ScenarioCategory.GOVERNMENT],
        "police": [ScenarioCategory.GOVERNMENT],
        "online": [ScenarioCategory.DIGITAL],
        "internet": [ScenarioCategory.DIGITAL],
        "digital": [ScenarioCategory.DIGITAL],
        "data": [ScenarioCategory.DIGITAL],
        "social media": [ScenarioCategory.DIGITAL],
        "health": [ScenarioCategory.HEALTHCARE],
        "medical": [ScenarioCategory.HEALTHCARE],
        "hospital": [ScenarioCategory.HEALTHCARE],
        "doctor": [ScenarioCategory.HEALTHCARE],
        "school": [ScenarioCategory.EDUCATION],
        "education": [ScenarioCategory.EDUCATION],
        "student": [ScenarioCategory.EDUCATION],
        "university": [ScenarioCategory.EDUCATION],
        "housing": [ScenarioCategory.HOUSING],
        "home": [ScenarioCategory.HOUSING],
        "rent": [ScenarioCategory.HOUSING],
        "property": [ScenarioCategory.HOUSING, ScenarioCategory.COMMERCE],
        "transport": [ScenarioCategory.TRANSPORT],
        "travel": [ScenarioCategory.TRANSPORT],
        "movement": [ScenarioCategory.TRANSPORT],
    }

    def __init__(self, seed: Optional[int] = None):
        """Initialize the scenario generator.

        Args:
            seed: Optional random seed for reproducibility.
        """
        if seed is not None:
            random.seed(seed)
        self._used_scenarios: set[str] = set()

    def generate_scenario(
        self,
        category: Optional[ScenarioCategory] = None,
        keywords: Optional[list[str]] = None,
        avoid_recent: bool = True
    ) -> Scenario:
        """Generate a relatable scenario.

        Args:
            category: Optional specific category.
            keywords: Optional keywords to match.
            avoid_recent: Whether to avoid recently used scenarios.

        Returns:
            A generated Scenario.
        """
        # Determine category
        if category is None:
            if keywords:
                category = self._match_category_to_keywords(keywords)
            else:
                category = random.choice(list(ScenarioCategory))

        # Get templates for category
        templates = self.SCENARIO_TEMPLATES.get(category, [])
        if not templates:
            templates = self.SCENARIO_TEMPLATES[ScenarioCategory.COMMUNITY]

        # Filter out recent scenarios if requested
        if avoid_recent:
            available = [
                t for t in templates
                if t["setup"] not in self._used_scenarios
            ]
            if not available:
                self._used_scenarios.clear()
                available = templates
        else:
            available = templates

        # Select template
        template = random.choice(available)
        self._used_scenarios.add(template["setup"])

        return Scenario(
            category=category,
            setup=template["setup"],
            characters=template["characters"],
            setting=template["setting"],
            conflict=template.get("conflict"),
            keywords=template.get("keywords", [])
        )

    def get_temporal_hook(
        self,
        target_date: Optional[date] = None
    ) -> Optional[TemporalHook]:
        """Get a date-aware contextual hook.

        Args:
            target_date: The date to check (defaults to today).

        Returns:
            TemporalHook if relevant occasion found, else None.
        """
        target_date = target_date or datetime.now().date()
        month = target_date.month

        occasions = self.TEMPORAL_OCCASIONS.get(month, [])
        if not occasions:
            return None

        occasion = random.choice(occasions)
        return TemporalHook(
            date=target_date,
            occasion=occasion["occasion"],
            relevance=occasion["relevance"],
            suggested_angle=occasion["angle"]
        )

    def match_scenario_to_topic(
        self,
        topic: str,
        section_keywords: Optional[list[str]] = None
    ) -> Scenario:
        """Find a relevant scenario for a topic.

        Args:
            topic: The topic text.
            section_keywords: Optional keywords from document section.

        Returns:
            A matched Scenario.
        """
        # Combine topic and section keywords
        all_keywords = []
        if section_keywords:
            all_keywords.extend(section_keywords)

        # Extract keywords from topic
        topic_lower = topic.lower()
        for keyword, categories in self.KEYWORD_CATEGORIES.items():
            if keyword in topic_lower:
                all_keywords.append(keyword)

        return self.generate_scenario(keywords=all_keywords if all_keywords else None)

    def get_scenario_for_insight(
        self,
        insight_keywords: list[str],
        avoid_category: Optional[ScenarioCategory] = None
    ) -> Scenario:
        """Get a scenario that matches an insight's keywords.

        Args:
            insight_keywords: Keywords from the insight.
            avoid_category: Category to avoid for variety.

        Returns:
            Matched Scenario.
        """
        # Match category
        category = self._match_category_to_keywords(insight_keywords)

        # Avoid if requested
        if avoid_category and category == avoid_category:
            categories = list(ScenarioCategory)
            categories.remove(avoid_category)
            category = random.choice(categories)

        return self.generate_scenario(category=category, keywords=insight_keywords)

    def get_scenarios_for_thread(
        self,
        num_scenarios: int,
        topic_keywords: Optional[list[str]] = None
    ) -> list[Scenario]:
        """Get multiple distinct scenarios for a thread.

        Args:
            num_scenarios: Number of scenarios to generate.
            topic_keywords: Optional topic keywords.

        Returns:
            List of distinct Scenarios.
        """
        scenarios = []
        used_categories: set[ScenarioCategory] = set()

        for _ in range(num_scenarios):
            # Try to use different categories
            available_categories = [
                c for c in ScenarioCategory
                if c not in used_categories
            ]

            if not available_categories:
                available_categories = list(ScenarioCategory)

            category = random.choice(available_categories)
            used_categories.add(category)

            scenario = self.generate_scenario(
                category=category,
                keywords=topic_keywords
            )
            scenarios.append(scenario)

        return scenarios

    def _match_category_to_keywords(
        self,
        keywords: list[str]
    ) -> ScenarioCategory:
        """Match keywords to the best scenario category.

        Args:
            keywords: List of keywords to match.

        Returns:
            Best matching ScenarioCategory.
        """
        category_scores: dict[ScenarioCategory, int] = {}

        for keyword in keywords:
            keyword_lower = keyword.lower()
            for kw, categories in self.KEYWORD_CATEGORIES.items():
                if kw in keyword_lower or keyword_lower in kw:
                    for cat in categories:
                        category_scores[cat] = category_scores.get(cat, 0) + 1

        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]

        return random.choice(list(ScenarioCategory))

    def get_random_category(self) -> ScenarioCategory:
        """Get a random scenario category."""
        return random.choice(list(ScenarioCategory))

    def get_all_categories(self) -> list[ScenarioCategory]:
        """Get all available scenario categories."""
        return list(ScenarioCategory)

    def clear_used_scenarios(self) -> None:
        """Clear the used scenarios cache."""
        self._used_scenarios.clear()
