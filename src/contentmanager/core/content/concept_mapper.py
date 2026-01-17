"""Concept mapper for connecting topics to constitutional principles.

This module enables the bot to think conceptually - connecting social/political
topics to relevant constitutional values even when exact text matches don't exist.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ConstitutionalPrinciple(Enum):
    """Core constitutional principles and rights."""
    HUMAN_DIGNITY = "human_dignity"
    EQUALITY = "equality"
    FREEDOM_EXPRESSION = "freedom_expression"
    FREEDOM_MOVEMENT = "freedom_movement"
    FREEDOM_ASSOCIATION = "freedom_association"
    FREEDOM_RELIGION = "freedom_religion"
    RIGHT_TO_LIFE = "right_to_life"
    SECURITY_OF_PERSON = "security_of_person"
    PRIVACY = "privacy"
    ACCESS_TO_INFORMATION = "access_to_information"
    JUST_ADMINISTRATIVE_ACTION = "just_administrative_action"
    PROPERTY_RIGHTS = "property_rights"
    HOUSING = "housing"
    HEALTHCARE = "healthcare"
    FOOD_WATER = "food_water"
    SOCIAL_SECURITY = "social_security"
    CHILDREN_RIGHTS = "children_rights"
    EDUCATION = "education"
    LANGUAGE_CULTURE = "language_culture"
    ENVIRONMENT = "environment"
    ACCESS_TO_COURTS = "access_to_courts"
    ARRESTED_PERSONS = "arrested_persons"
    FAIR_TRIAL = "fair_trial"
    DEMOCRATIC_PARTICIPATION = "democratic_participation"


@dataclass
class ConceptMapping:
    """Maps a topic to related constitutional principles."""
    topic: str
    principles: list[ConstitutionalPrinciple]
    section_references: list[int]  # Relevant section numbers
    key_concepts: list[str]  # Related concepts to explore
    perspective_angles: list[str]  # Different angles to approach the topic
    real_world_connections: list[str]  # How this manifests in real life


# Knowledge base mapping topics to constitutional concepts
TOPIC_CONCEPT_MAP: dict[str, ConceptMapping] = {
    # Social Issues
    "xenophobia": ConceptMapping(
        topic="xenophobia",
        principles=[
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.EQUALITY,
            ConstitutionalPrinciple.SECURITY_OF_PERSON,
            ConstitutionalPrinciple.FREEDOM_MOVEMENT,
        ],
        section_references=[9, 10, 12, 21],
        key_concepts=[
            "non-discrimination", "human dignity", "equal protection",
            "freedom from violence", "right to move freely"
        ],
        perspective_angles=[
            "How dignity applies to everyone regardless of nationality",
            "The equality clause protects all people in SA, not just citizens",
            "Violence against foreigners violates security of person rights",
            "The tension between national identity and universal human rights"
        ],
        real_world_connections=[
            "Attacks on foreign-owned shops", "Discrimination in hiring",
            "Access to services for non-citizens", "Community tensions"
        ]
    ),
    "illegal foreigners": ConceptMapping(
        topic="illegal foreigners",
        principles=[
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.EQUALITY,
            ConstitutionalPrinciple.SECURITY_OF_PERSON,
            ConstitutionalPrinciple.JUST_ADMINISTRATIVE_ACTION,
        ],
        section_references=[9, 10, 12, 33],
        key_concepts=[
            "human dignity regardless of status", "equal protection under law",
            "constitutional rights vs citizenship rights", "due process",
            "administrative justice in immigration matters"
        ],
        perspective_angles=[
            "The Constitution protects human dignity for ALL people, not just citizens",
            "Section 9 equality rights apply to everyone in South Africa",
            "Even undocumented persons have constitutional protections",
            "The difference between human rights and citizenship privileges"
        ],
        real_world_connections=[
            "Deportation procedures", "Access to emergency healthcare",
            "Treatment in detention", "Children's rights regardless of parents' status"
        ]
    ),
    "foreigners": ConceptMapping(
        topic="foreigners",
        principles=[
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.EQUALITY,
            ConstitutionalPrinciple.SECURITY_OF_PERSON,
            ConstitutionalPrinciple.FREEDOM_MOVEMENT,
        ],
        section_references=[9, 10, 12, 21],
        key_concepts=[
            "non-discrimination", "human dignity", "equal protection",
            "freedom from violence", "universal human rights"
        ],
        perspective_angles=[
            "Constitutional rights that apply to everyone, not just citizens",
            "The Bill of Rights protects 'everyone' - a deliberate word choice",
            "Human dignity as the foundation of all other rights",
            "Integration vs exclusion in a constitutional democracy"
        ],
        real_world_connections=[
            "Foreign nationals living in SA", "Refugee rights",
            "Access to services", "Community integration"
        ]
    ),
    "migrants": ConceptMapping(
        topic="migrants",
        principles=[
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.EQUALITY,
            ConstitutionalPrinciple.FREEDOM_MOVEMENT,
            ConstitutionalPrinciple.CHILDREN_RIGHTS,
        ],
        section_references=[9, 10, 21, 28],
        key_concepts=[
            "freedom of movement", "human dignity", "children's best interests",
            "non-discrimination", "access to basic services"
        ],
        perspective_angles=[
            "Section 21 on freedom of movement and residence",
            "Children's constitutional rights regardless of parents' migration status",
            "Human dignity as non-negotiable regardless of documentation",
            "The constitutional vision of an inclusive society"
        ],
        real_world_connections=[
            "Migrant workers' rights", "Refugee children in schools",
            "Healthcare access", "Labor protections"
        ]
    ),
    "racism": ConceptMapping(
        topic="racism",
        principles=[
            ConstitutionalPrinciple.EQUALITY,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.FREEDOM_EXPRESSION,
        ],
        section_references=[9, 10, 16],
        key_concepts=[
            "non-discrimination on grounds of race", "unfair discrimination",
            "equality before the law", "hate speech limits"
        ],
        perspective_angles=[
            "Section 9 explicitly prohibits discrimination based on race",
            "The Constitution's vision of a non-racial society",
            "Balancing free speech with protection from hate speech",
            "Historical context: from apartheid to constitutional equality"
        ],
        real_world_connections=[
            "Workplace discrimination", "Unequal service delivery",
            "Racist speech on social media", "Redress and affirmative action"
        ]
    ),
    "gender equality": ConceptMapping(
        topic="gender equality",
        principles=[
            ConstitutionalPrinciple.EQUALITY,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.FREEDOM_ASSOCIATION,
        ],
        section_references=[9, 10, 18],
        key_concepts=[
            "non-discrimination on grounds of sex, gender, sexual orientation",
            "substantive equality", "equal treatment", "affirmative action"
        ],
        perspective_angles=[
            "Section 9(3) protects against gender-based discrimination",
            "Substantive vs formal equality - what real equality looks like",
            "Cultural practices vs constitutional rights",
            "LGBTQ+ rights under the equality clause"
        ],
        real_world_connections=[
            "Gender pay gap", "GBV and the state's duty to protect",
            "Women in leadership", "Trans rights and recognition"
        ]
    ),
    "corruption": ConceptMapping(
        topic="corruption",
        principles=[
            ConstitutionalPrinciple.JUST_ADMINISTRATIVE_ACTION,
            ConstitutionalPrinciple.ACCESS_TO_INFORMATION,
            ConstitutionalPrinciple.DEMOCRATIC_PARTICIPATION,
        ],
        section_references=[32, 33, 195],
        key_concepts=[
            "accountability", "transparency", "public administration values",
            "access to information", "lawful administrative action"
        ],
        perspective_angles=[
            "Section 195 requires efficient, ethical public administration",
            "Access to information as a corruption-fighting tool",
            "Administrative justice protects against arbitrary decisions",
            "The link between corruption and service delivery failures"
        ],
        real_world_connections=[
            "State capture", "Tender fraud", "Municipal corruption",
            "Whistleblower protection"
        ]
    ),
    "unemployment": ConceptMapping(
        topic="unemployment",
        principles=[
            ConstitutionalPrinciple.SOCIAL_SECURITY,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.EQUALITY,
        ],
        section_references=[10, 27, 9],
        key_concepts=[
            "right to social security", "progressive realization",
            "dignity in economic hardship", "equal access to opportunities"
        ],
        perspective_angles=[
            "Section 27 includes rights to social security",
            "Human dignity even when unemployed",
            "The state's duty to address unemployment progressively",
            "Discrimination in hiring practices"
        ],
        real_world_connections=[
            "SASSA grants", "Youth unemployment crisis",
            "Skills development programs", "UIF system"
        ]
    ),
    "housing": ConceptMapping(
        topic="housing",
        principles=[
            ConstitutionalPrinciple.HOUSING,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.PROPERTY_RIGHTS,
        ],
        section_references=[26, 10, 25],
        key_concepts=[
            "right to adequate housing", "progressive realization",
            "no arbitrary eviction", "dignity in housing"
        ],
        perspective_angles=[
            "Section 26 guarantees access to adequate housing",
            "The state's duty to progressively realize housing rights",
            "Protection against arbitrary evictions",
            "Balancing property rights with housing needs"
        ],
        real_world_connections=[
            "RDP housing", "Informal settlements", "Eviction cases",
            "Land reform", "Affordable housing crisis"
        ]
    ),
    "load shedding": ConceptMapping(
        topic="load shedding",
        principles=[
            ConstitutionalPrinciple.JUST_ADMINISTRATIVE_ACTION,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.HEALTHCARE,
            ConstitutionalPrinciple.EDUCATION,
        ],
        section_references=[33, 10, 27, 29],
        key_concepts=[
            "reasonable administrative action", "service delivery",
            "impact on healthcare", "impact on education"
        ],
        perspective_angles=[
            "Administrative decisions affecting millions",
            "How power cuts impact dignity and basic rights",
            "Healthcare services during load shedding",
            "Education disruption and learners' rights"
        ],
        real_world_connections=[
            "Hospital equipment failures", "Business closures",
            "School disruptions", "Security concerns in darkness"
        ]
    ),
    "gbv": ConceptMapping(
        topic="gender-based violence",
        principles=[
            ConstitutionalPrinciple.SECURITY_OF_PERSON,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.EQUALITY,
            ConstitutionalPrinciple.RIGHT_TO_LIFE,
        ],
        section_references=[12, 10, 9, 11],
        key_concepts=[
            "freedom and security of person", "right to bodily integrity",
            "state's duty to protect", "violence-free existence"
        ],
        perspective_angles=[
            "Section 12's guarantee of security and bodily integrity",
            "The state's constitutional duty to protect people from violence",
            "GBV as a violation of equality and dignity",
            "Children's vulnerability and special protection"
        ],
        real_world_connections=[
            "Femicide statistics", "Protection orders", "Police response",
            "Shelters and support services"
        ]
    ),
    "hate speech": ConceptMapping(
        topic="hate speech",
        principles=[
            ConstitutionalPrinciple.FREEDOM_EXPRESSION,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.EQUALITY,
        ],
        section_references=[16, 10, 9],
        key_concepts=[
            "limits on free speech", "incitement to harm",
            "propaganda for war", "advocacy of hatred"
        ],
        perspective_angles=[
            "Section 16 protects speech but excludes hate speech",
            "The balance between free expression and protection from hatred",
            "Difference between offensive speech and hate speech",
            "Online hate speech challenges"
        ],
        real_world_connections=[
            "Social media incidents", "Court cases on hate speech",
            "Political rhetoric", "Religious tensions"
        ]
    ),
    "privacy": ConceptMapping(
        topic="privacy",
        principles=[
            ConstitutionalPrinciple.PRIVACY,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.ACCESS_TO_INFORMATION,
        ],
        section_references=[14, 10, 32],
        key_concepts=[
            "right to privacy", "protection of personal information",
            "search and seizure", "communications privacy"
        ],
        perspective_angles=[
            "Section 14's comprehensive privacy protection",
            "Privacy in the digital age",
            "Balancing privacy with transparency and security",
            "POPIA and constitutional privacy rights"
        ],
        real_world_connections=[
            "Data breaches", "Surveillance concerns", "Social media privacy",
            "Employer monitoring"
        ]
    ),
    "police brutality": ConceptMapping(
        topic="police brutality",
        principles=[
            ConstitutionalPrinciple.SECURITY_OF_PERSON,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.ARRESTED_PERSONS,
            ConstitutionalPrinciple.RIGHT_TO_LIFE,
        ],
        section_references=[12, 10, 35, 11],
        key_concepts=[
            "freedom from torture", "cruel treatment prohibition",
            "rights of arrested persons", "use of force limits"
        ],
        perspective_angles=[
            "Section 12 protects against torture and cruel treatment",
            "Arrested persons' rights under Section 35",
            "Police accountability and constitutional limits",
            "The dignity of all persons, including suspects"
        ],
        real_world_connections=[
            "Deaths in custody", "Protest policing", "IPID investigations",
            "Community-police relations"
        ]
    ),
    "water": ConceptMapping(
        topic="water access",
        principles=[
            ConstitutionalPrinciple.FOOD_WATER,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.ENVIRONMENT,
        ],
        section_references=[27, 10, 24],
        key_concepts=[
            "right to water", "progressive realization",
            "environmental sustainability", "dignity in access"
        ],
        perspective_angles=[
            "Section 27 includes the right to sufficient water",
            "The state's duty to progressively ensure water access",
            "Environmental protection and water resources",
            "Water as essential for dignity and life"
        ],
        real_world_connections=[
            "Water cuts in communities", "Dam levels", "Water pollution",
            "Billing and affordability"
        ]
    ),
    "education": ConceptMapping(
        topic="education",
        principles=[
            ConstitutionalPrinciple.EDUCATION,
            ConstitutionalPrinciple.CHILDREN_RIGHTS,
            ConstitutionalPrinciple.LANGUAGE_CULTURE,
            ConstitutionalPrinciple.EQUALITY,
        ],
        section_references=[29, 28, 30, 31, 9],
        key_concepts=[
            "right to basic education", "language in education",
            "children's best interests", "equal access"
        ],
        perspective_angles=[
            "Section 29's guarantee of basic education",
            "Language rights in schools",
            "Quality vs access in education",
            "Children's constitutional protection"
        ],
        real_world_connections=[
            "School infrastructure", "Textbook delivery", "Language policies",
            "Fees and accessibility"
        ]
    ),
    "freedom of speech": ConceptMapping(
        topic="freedom of speech",
        principles=[
            ConstitutionalPrinciple.FREEDOM_EXPRESSION,
            ConstitutionalPrinciple.FREEDOM_ASSOCIATION,
            ConstitutionalPrinciple.ACCESS_TO_INFORMATION,
        ],
        section_references=[16, 18, 32],
        key_concepts=[
            "freedom of expression", "media freedom", "artistic freedom",
            "academic freedom", "limits on speech"
        ],
        perspective_angles=[
            "Section 16's broad protection of expression",
            "What speech is NOT protected",
            "Media freedom and democracy",
            "Online expression in the modern age"
        ],
        real_world_connections=[
            "Journalist harassment", "Social media debates",
            "Art censorship attempts", "Academic freedom cases"
        ]
    ),
    "protest": ConceptMapping(
        topic="protest",
        principles=[
            ConstitutionalPrinciple.FREEDOM_ASSOCIATION,
            ConstitutionalPrinciple.FREEDOM_EXPRESSION,
            ConstitutionalPrinciple.DEMOCRATIC_PARTICIPATION,
        ],
        section_references=[17, 16, 19],
        key_concepts=[
            "right to assemble peacefully", "right to demonstrate",
            "right to picket", "unarmed gathering"
        ],
        perspective_angles=[
            "Section 17 protects peaceful protest",
            "The 'peaceful and unarmed' requirement",
            "Protest as democratic expression",
            "Balancing protest rights with public order"
        ],
        real_world_connections=[
            "Service delivery protests", "Student movements",
            "Worker strikes", "Political demonstrations"
        ]
    ),
}


# Keywords that can trigger concept matching
KEYWORD_CONCEPT_MAP: dict[str, list[str]] = {
    "foreigner": ["xenophobia"],
    "foreigners": ["xenophobia"],
    "illegal": ["xenophobia"],
    "undocumented": ["xenophobia"],
    "migrant": ["xenophobia"],
    "migrants": ["xenophobia"],
    "immigrant": ["xenophobia"],
    "immigrants": ["xenophobia"],
    "refugee": ["xenophobia"],
    "refugees": ["xenophobia"],
    "asylum": ["xenophobia"],
    "non-citizen": ["xenophobia"],
    "non-citizens": ["xenophobia"],
    "african": ["xenophobia", "racism"],
    "discrimination": ["racism", "gender equality", "equality"],
    "race": ["racism"],
    "racial": ["racism"],
    "women": ["gender equality", "gbv"],
    "woman": ["gender equality", "gbv"],
    "lgbtq": ["gender equality"],
    "gay": ["gender equality"],
    "lesbian": ["gender equality"],
    "transgender": ["gender equality"],
    "corrupt": ["corruption"],
    "bribe": ["corruption"],
    "tender": ["corruption"],
    "state capture": ["corruption"],
    "jobs": ["unemployment"],
    "employ": ["unemployment"],
    "work": ["unemployment"],
    "eskom": ["load shedding"],
    "electricity": ["load shedding"],
    "power cut": ["load shedding"],
    "blackout": ["load shedding"],
    "house": ["housing"],
    "evict": ["housing"],
    "shack": ["housing"],
    "informal settlement": ["housing"],
    "violence": ["gbv", "police brutality"],
    "abuse": ["gbv"],
    "femicide": ["gbv"],
    "domestic": ["gbv"],
    "hate": ["hate speech"],
    "speech": ["hate speech", "freedom of speech"],
    "express": ["freedom of speech"],
    "censor": ["freedom of speech"],
    "privacy": ["privacy"],
    "data": ["privacy"],
    "surveillance": ["privacy"],
    "police": ["police brutality"],
    "brutality": ["police brutality"],
    "arrest": ["police brutality"],
    "custody": ["police brutality"],
    "water": ["water"],
    "tap": ["water"],
    "school": ["education"],
    "learn": ["education"],
    "teach": ["education"],
    "university": ["education"],
    "march": ["protest"],
    "strike": ["protest"],
    "demonstrate": ["protest"],
    "picket": ["protest"],
}


class ConceptMapper:
    """Maps topics and keywords to constitutional concepts."""

    def __init__(self):
        self.topic_map = TOPIC_CONCEPT_MAP
        self.keyword_map = KEYWORD_CONCEPT_MAP

    def map_topic(self, topic: str) -> Optional[ConceptMapping]:
        """Map a topic to constitutional concepts.

        Args:
            topic: The topic to map (e.g., "xenophobia", "corruption")

        Returns:
            ConceptMapping if found, None otherwise
        """
        topic_lower = topic.lower().strip()

        # Direct match
        if topic_lower in self.topic_map:
            return self.topic_map[topic_lower]

        # Partial match in topic names
        for key, mapping in self.topic_map.items():
            if topic_lower in key or key in topic_lower:
                return mapping

        # Keyword-based matching
        matched_topics = set()
        for word in topic_lower.split():
            if word in self.keyword_map:
                matched_topics.update(self.keyword_map[word])

        if matched_topics:
            # Return the first matched topic's mapping
            for matched in matched_topics:
                if matched in self.topic_map:
                    return self.topic_map[matched]

        return None

    def get_related_sections(self, topic: str) -> list[int]:
        """Get section numbers related to a topic.

        Args:
            topic: The topic to get sections for

        Returns:
            List of section numbers
        """
        mapping = self.map_topic(topic)
        return mapping.section_references if mapping else []

    def get_key_concepts(self, topic: str) -> list[str]:
        """Get key concepts related to a topic.

        Args:
            topic: The topic to get concepts for

        Returns:
            List of key concepts
        """
        mapping = self.map_topic(topic)
        return mapping.key_concepts if mapping else []

    def get_perspective_angles(self, topic: str) -> list[str]:
        """Get different angles to approach a topic.

        Args:
            topic: The topic to get angles for

        Returns:
            List of perspective angles
        """
        mapping = self.map_topic(topic)
        return mapping.perspective_angles if mapping else []

    def build_context_for_synthesis(self, topic: str) -> str:
        """Build a rich context for content synthesis from concept mapping.

        Args:
            topic: The topic to build context for

        Returns:
            Formatted context string for LLM prompts
        """
        mapping = self.map_topic(topic)
        if not mapping:
            return ""

        lines = [
            f"Topic: {topic}",
            "",
            "Related Constitutional Principles:",
        ]

        for principle in mapping.principles:
            lines.append(f"  - {principle.value.replace('_', ' ').title()}")

        lines.extend([
            "",
            f"Relevant Sections: {', '.join(f'Section {n}' for n in mapping.section_references)}",
            "",
            "Key Concepts:",
        ])

        for concept in mapping.key_concepts:
            lines.append(f"  - {concept}")

        lines.extend([
            "",
            "Perspective Angles:",
        ])

        for angle in mapping.perspective_angles:
            lines.append(f"  - {angle}")

        lines.extend([
            "",
            "Real-World Connections:",
        ])

        for connection in mapping.real_world_connections:
            lines.append(f"  - {connection}")

        return "\n".join(lines)

    def get_all_topics(self) -> list[str]:
        """Get all mapped topics."""
        return list(self.topic_map.keys())

    def add_topic_mapping(self, mapping: ConceptMapping) -> None:
        """Add a new topic mapping.

        Args:
            mapping: The concept mapping to add
        """
        self.topic_map[mapping.topic.lower()] = mapping
