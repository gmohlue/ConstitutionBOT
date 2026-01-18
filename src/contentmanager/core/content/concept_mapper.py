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
    "constitutional accountability": ConceptMapping(
        topic="constitutional accountability",
        principles=[
            ConstitutionalPrinciple.JUST_ADMINISTRATIVE_ACTION,
            ConstitutionalPrinciple.ACCESS_TO_INFORMATION,
            ConstitutionalPrinciple.DEMOCRATIC_PARTICIPATION,
            ConstitutionalPrinciple.ACCESS_TO_COURTS,
        ],
        section_references=[1, 2, 33, 34, 55, 92, 181, 195],
        key_concepts=[
            "constitutional supremacy", "rule of law", "public accountability",
            "separation of powers", "checks and balances", "judicial review",
            "executive accountability to Parliament", "Chapter 9 institutions"
        ],
        perspective_angles=[
            "Section 1 establishes constitutional supremacy - no one is above the law",
            "Section 2 makes the Constitution the supreme law that binds all",
            "The executive must account to Parliament (Section 92)",
            "Chapter 9 institutions (Public Protector, Auditor-General) ensure accountability",
            "Courts can review any government action for constitutionality"
        ],
        real_world_connections=[
            "Nkandla judgment", "State of Capture report", "Court challenges to government",
            "Parliamentary oversight", "Public Protector investigations", "Auditor-General reports"
        ]
    ),
    "accountability": ConceptMapping(
        topic="accountability",
        principles=[
            ConstitutionalPrinciple.JUST_ADMINISTRATIVE_ACTION,
            ConstitutionalPrinciple.ACCESS_TO_INFORMATION,
            ConstitutionalPrinciple.DEMOCRATIC_PARTICIPATION,
        ],
        section_references=[1, 33, 92, 181, 195],
        key_concepts=[
            "rule of law", "public accountability", "transparency",
            "responsive government", "ethical conduct", "Chapter 9 institutions"
        ],
        perspective_angles=[
            "Everyone, including government, is bound by the Constitution",
            "Section 195 values: accountability, transparency, efficiency",
            "The executive's accountability to the legislature",
            "Independent institutions that hold power to account"
        ],
        real_world_connections=[
            "Parliamentary questions", "Public Protector complaints",
            "Auditor-General findings", "Court orders against government"
        ]
    ),
    "government accountability": ConceptMapping(
        topic="government accountability",
        principles=[
            ConstitutionalPrinciple.JUST_ADMINISTRATIVE_ACTION,
            ConstitutionalPrinciple.ACCESS_TO_INFORMATION,
            ConstitutionalPrinciple.DEMOCRATIC_PARTICIPATION,
        ],
        section_references=[33, 55, 92, 181, 195],
        key_concepts=[
            "executive accountability", "parliamentary oversight",
            "public administration values", "Chapter 9 institutions",
            "responsive, accountable governance"
        ],
        perspective_angles=[
            "Cabinet members are accountable to Parliament (Section 92)",
            "National Assembly holds executive to account (Section 55)",
            "Public administration must be accountable (Section 195)",
            "Chapter 9 institutions provide independent oversight"
        ],
        real_world_connections=[
            "Cabinet question time", "Portfolio committee hearings",
            "Motions of no confidence", "Public Protector reports"
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
    # ========================================================================
    # SA TREND TOPICS - Real discourse from South African social/political life
    # ========================================================================
    "sassa_grants": ConceptMapping(
        topic="SASSA grants",
        principles=[
            ConstitutionalPrinciple.SOCIAL_SECURITY,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.JUST_ADMINISTRATIVE_ACTION,
            ConstitutionalPrinciple.CHILDREN_RIGHTS,
        ],
        section_references=[27, 10, 33, 28],
        key_concepts=[
            "right to social security", "social assistance",
            "administrative justice in grant applications",
            "dignity in accessing state support", "child support"
        ],
        perspective_angles=[
            "Section 27 guarantees the right to social security",
            "The SASSA queue as a test of constitutional promises",
            "Administrative justice when your grant is suspended",
            "What dignity looks like when you need government help"
        ],
        real_world_connections=[
            "Grant payment day queues", "SASSA card problems",
            "R350 SRD grant applications", "Child support grants",
            "Grant suspension without notice", "Lapsed grants",
            "Disability grant assessments", "Foster care grants"
        ]
    ),
    "nsfas": ConceptMapping(
        topic="NSFAS",
        principles=[
            ConstitutionalPrinciple.EDUCATION,
            ConstitutionalPrinciple.EQUALITY,
            ConstitutionalPrinciple.JUST_ADMINISTRATIVE_ACTION,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
        ],
        section_references=[29, 9, 33, 10],
        key_concepts=[
            "right to further education", "progressive access",
            "equal educational opportunity", "administrative fairness",
            "student funding as constitutional right"
        ],
        perspective_angles=[
            "Section 29 and the state's duty to make education accessible",
            "When your NSFAS status says 'provisionally funded' for months",
            "Equality in education - does money determine who studies?",
            "The gap between constitutional promises and registration day reality"
        ],
        real_world_connections=[
            "NSFAS portal crashes", "Allowance payment delays",
            "Registration blocked for funding status", "Missing meal allowances",
            "Accommodation funding gaps", "Historic debt and registration",
            "Appeals process failures", "First-generation students"
        ]
    ),
    "municipality_failures": ConceptMapping(
        topic="municipality failures",
        principles=[
            ConstitutionalPrinciple.JUST_ADMINISTRATIVE_ACTION,
            ConstitutionalPrinciple.FOOD_WATER,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.HOUSING,
        ],
        section_references=[33, 27, 10, 26, 152, 153],
        key_concepts=[
            "local government obligations", "service delivery",
            "reasonable administrative action", "basic services as rights",
            "municipal accountability", "cooperative governance"
        ],
        perspective_angles=[
            "Section 152 mandates municipalities to provide services",
            "What happens when your water bill is wrong but no one answers",
            "Administrative justice when the municipality ignores you",
            "Your constitutional rights don't disappear at the municipal office door"
        ],
        real_world_connections=[
            "Burst pipes going unfixed for weeks", "Electricity prepaid meter errors",
            "Refuse collection stopping", "Pothole damage claims ignored",
            "Building plan approvals taking years", "Rates queries unanswered",
            "Councillors unreachable", "Municipal strike impacts"
        ]
    ),
    "youth_unemployment": ConceptMapping(
        topic="youth unemployment",
        principles=[
            ConstitutionalPrinciple.SOCIAL_SECURITY,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.EQUALITY,
            ConstitutionalPrinciple.EDUCATION,
        ],
        section_references=[27, 10, 9, 29, 22],
        key_concepts=[
            "dignity without employment", "equal opportunity",
            "right to choose occupation", "state duty to address unemployment",
            "social security for the unemployed"
        ],
        perspective_angles=[
            "What does dignity mean when you've sent 500 CVs with no response?",
            "Section 22's right to choose your trade - but what if there's no work?",
            "The equality clause and unpaid internships only for those who can afford them",
            "When qualifications don't translate to employment"
        ],
        real_world_connections=[
            "Matric results vs job reality", "Graduate unemployment",
            "EPWP temporary jobs", "Youth wage subsidy", "Internship exploitation",
            "CV dropping", "LinkedIn vs actual hiring", "Nepotism in hiring"
        ]
    ),
    "digital_divide": ConceptMapping(
        topic="digital divide",
        principles=[
            ConstitutionalPrinciple.ACCESS_TO_INFORMATION,
            ConstitutionalPrinciple.EDUCATION,
            ConstitutionalPrinciple.EQUALITY,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
        ],
        section_references=[32, 29, 9, 10],
        key_concepts=[
            "right to access information", "education in digital age",
            "equality in information access", "digital as essential service",
            "data costs and constitutional rights"
        ],
        perspective_angles=[
            "Section 32's access to information in a world that assumes you have data",
            "When 'apply online' excludes those without connectivity",
            "Educational equality when learning moved to WhatsApp",
            "Is expensive data a barrier to constitutional rights?"
        ],
        real_world_connections=[
            "Data costs for job applications", "Online learning during COVID",
            "No signal in rural areas", "Smartphone requirement for services",
            "WhatsApp for school communication", "E-government excluding citizens",
            "Banking apps required for grants", "Library internet access"
        ]
    ),
    "taxi_industry": ConceptMapping(
        topic="taxi industry",
        principles=[
            ConstitutionalPrinciple.FREEDOM_MOVEMENT,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.SECURITY_OF_PERSON,
            ConstitutionalPrinciple.RIGHT_TO_LIFE,
        ],
        section_references=[21, 10, 12, 11],
        key_concepts=[
            "freedom of movement", "dignity in transport",
            "safety in public transport", "right to life on the roads",
            "commuter rights"
        ],
        perspective_angles=[
            "Section 21 freedom of movement - but at what cost and risk?",
            "Dignity in the daily commute - overloading, routes, fares",
            "Right to life when taxi violence flares",
            "The state's duty to regulate for safety vs lived reality"
        ],
        real_world_connections=[
            "Taxi fare increases", "Route conflicts", "Taxi violence",
            "Overloading", "Long-distance taxi safety", "Taxi rank conditions",
            "Early morning commutes", "Last-taxi anxiety", "Taxi strikes"
        ]
    ),
    "clinic_queues": ConceptMapping(
        topic="clinic queues",
        principles=[
            ConstitutionalPrinciple.HEALTHCARE,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.JUST_ADMINISTRATIVE_ACTION,
            ConstitutionalPrinciple.CHILDREN_RIGHTS,
        ],
        section_references=[27, 10, 33, 28],
        key_concepts=[
            "right to healthcare access", "dignity in healthcare",
            "reasonable access to services", "emergency medical treatment",
            "children's health rights"
        ],
        perspective_angles=[
            "Section 27 says you have the right to healthcare - but how long is the queue?",
            "Dignity when you're turned away because 'files are finished'",
            "Administrative justice when your chronic medication runs out",
            "What 'progressive realization' means at 4am in the clinic queue"
        ],
        real_world_connections=[
            "4am clinic queues", "'Files finished' at 9am",
            "Chronic medication stock-outs", "Turned away without treatment",
            "Rude staff encounters", "No privacy during consultations",
            "Baby clinic days", "TB and HIV treatment access"
        ]
    ),
    "evictions": ConceptMapping(
        topic="evictions",
        principles=[
            ConstitutionalPrinciple.HOUSING,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.PROPERTY_RIGHTS,
            ConstitutionalPrinciple.CHILDREN_RIGHTS,
        ],
        section_references=[26, 10, 25, 28],
        key_concepts=[
            "protection against arbitrary eviction", "right to adequate housing",
            "court order requirement", "alternative accommodation",
            "balancing property rights and housing needs"
        ],
        perspective_angles=[
            "Section 26 says no one can be evicted without a court order",
            "What 'adequate housing' means when your shack is marked",
            "The red paint on the door - notice or threat?",
            "When your landlord changes the locks while you're at work"
        ],
        real_world_connections=[
            "Red-marked shacks", "Land invasions", "Landlord lockouts",
            "Back-room evictions", "Rental arrears during COVID",
            "Eviction in winter", "Where to go after eviction",
            "Children's schooling after eviction"
        ]
    ),
    "matric_exams": ConceptMapping(
        topic="matric exams",
        principles=[
            ConstitutionalPrinciple.EDUCATION,
            ConstitutionalPrinciple.EQUALITY,
            ConstitutionalPrinciple.JUST_ADMINISTRATIVE_ACTION,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
        ],
        section_references=[29, 9, 33, 10],
        key_concepts=[
            "right to basic education", "equal educational opportunity",
            "fair assessment processes", "remarking rights",
            "language in education"
        ],
        perspective_angles=[
            "Section 29 guarantees basic education - but does matric determine everything?",
            "Equality when some schools have and others don't",
            "Administrative justice in remarking and appeals",
            "The pressure cooker of matric and mental health"
        ],
        real_world_connections=[
            "Results day anxiety", "University admission cut-offs",
            "Remarking process", "No-fee schools vs former Model C",
            "Studying by candlelight during load shedding",
            "Teachers who disappeared", "NSC vs IEB debate"
        ]
    ),
    "femicide": ConceptMapping(
        topic="femicide",
        principles=[
            ConstitutionalPrinciple.RIGHT_TO_LIFE,
            ConstitutionalPrinciple.SECURITY_OF_PERSON,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.EQUALITY,
        ],
        section_references=[11, 12, 10, 9],
        key_concepts=[
            "right to life", "freedom from violence",
            "state's duty to protect", "gender-based violence",
            "dignity and bodily integrity"
        ],
        perspective_angles=[
            "Section 11's right to life and the state's failure to protect",
            "When reporting to SAPS doesn't stop the violence",
            "The gap between protection orders and actual protection",
            "Why another hashtag when the Constitution promises safety"
        ],
        real_world_connections=[
            "SAPS response to GBV reports", "Protection order enforcement",
            "Bail for perpetrators", "Court delays", "Victim-blaming responses",
            "Missing women cases", "Shelter availability", "Community responses"
        ]
    ),
    "correctional services": ConceptMapping(
        topic="correctional services",
        principles=[
            ConstitutionalPrinciple.ARRESTED_PERSONS,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.FAIR_TRIAL,
            ConstitutionalPrinciple.SECURITY_OF_PERSON,
        ],
        section_references=[35, 10, 12, 34],
        key_concepts=[
            "rights of detained persons", "right to humane conditions",
            "right to communicate with legal practitioner", "right to challenge detention",
            "presumption of innocence", "right to a fair trial"
        ],
        perspective_angles=[
            "Section 35 protects the rights of arrested, detained, and accused persons",
            "Detained persons retain their human dignity",
            "The right to humane conditions of detention",
            "Rehabilitation vs punishment in correctional services",
            "Access to legal representation as a fundamental right"
        ],
        real_world_connections=[
            "Prison overcrowding", "Awaiting-trial detainees",
            "Conditions in correctional facilities", "Parole and rehabilitation",
            "Treatment of remand detainees", "Access to healthcare in prisons"
        ]
    ),
    "prisons": ConceptMapping(
        topic="prisons",
        principles=[
            ConstitutionalPrinciple.ARRESTED_PERSONS,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.FAIR_TRIAL,
            ConstitutionalPrinciple.SECURITY_OF_PERSON,
        ],
        section_references=[35, 10, 12, 34],
        key_concepts=[
            "rights of detained persons", "humane detention conditions",
            "rehabilitation", "dignity in incarceration",
            "access to medical treatment", "contact with family"
        ],
        perspective_angles=[
            "Prisoners retain fundamental human rights",
            "Section 35(2) specifically protects detained persons",
            "The constitutional requirement for humane treatment",
            "Balancing security with human rights in detention"
        ],
        real_world_connections=[
            "Prison conditions", "Deaths in custody",
            "Rehabilitation programs", "Prison healthcare",
            "Rights of sentenced vs awaiting-trial prisoners"
        ]
    ),
    "detention": ConceptMapping(
        topic="detention",
        principles=[
            ConstitutionalPrinciple.ARRESTED_PERSONS,
            ConstitutionalPrinciple.HUMAN_DIGNITY,
            ConstitutionalPrinciple.SECURITY_OF_PERSON,
            ConstitutionalPrinciple.ACCESS_TO_COURTS,
        ],
        section_references=[35, 10, 12, 34],
        key_concepts=[
            "lawful detention", "right to challenge detention",
            "right to be brought before court", "conditions of detention",
            "right to legal representation", "no torture or cruel treatment"
        ],
        perspective_angles=[
            "Section 35(1) covers arrested persons' rights",
            "Section 35(2) covers detained persons' rights",
            "The right to be brought before court within 48 hours",
            "Habeas corpus and the right to challenge unlawful detention"
        ],
        real_world_connections=[
            "Police holding cells", "Immigration detention",
            "Remand detention", "Mental health detention",
            "Unlawful arrests"
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
    "accountability": ["accountability", "constitutional accountability"],
    "accountable": ["accountability", "constitutional accountability"],
    "oversight": ["accountability", "government accountability"],
    "chapter 9": ["constitutional accountability"],
    "public protector": ["constitutional accountability"],
    "auditor": ["constitutional accountability"],
    "parliament": ["government accountability"],
    "constitutional": ["constitutional accountability"],
    "supremacy": ["constitutional accountability"],
    "rule of law": ["constitutional accountability"],
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
    "prison": ["prisons", "correctional services"],
    "prisons": ["prisons", "correctional services"],
    "prisoner": ["prisons", "correctional services"],
    "prisoners": ["prisons", "correctional services"],
    "inmate": ["prisons", "correctional services"],
    "inmates": ["prisons", "correctional services"],
    "correctional": ["correctional services"],
    "corrections": ["correctional services"],
    "detain": ["detention"],
    "detained": ["detention"],
    "detainee": ["detention"],
    "detainees": ["detention"],
    "detention": ["detention"],
    "incarcerate": ["prisons", "correctional services"],
    "incarcerated": ["prisons", "correctional services"],
    "jail": ["detention", "prisons"],
    "remand": ["detention"],
    "awaiting trial": ["detention"],
    "accused": ["detention", "correctional services"],
    # SA trend topic keywords
    "sassa": ["sassa_grants"],
    "grant": ["sassa_grants", "social_security"],
    "grants": ["sassa_grants", "social_security"],
    "r350": ["sassa_grants"],
    "srd": ["sassa_grants"],
    "child support": ["sassa_grants"],
    "disability grant": ["sassa_grants"],
    "nsfas": ["nsfas"],
    "bursary": ["nsfas", "education"],
    "student funding": ["nsfas"],
    "allowance": ["nsfas"],
    "municipality": ["municipality_failures"],
    "municipal": ["municipality_failures"],
    "council": ["municipality_failures"],
    "rates": ["municipality_failures"],
    "pothole": ["municipality_failures"],
    "potholes": ["municipality_failures"],
    "refuse": ["municipality_failures"],
    "youth": ["youth_unemployment"],
    "job": ["youth_unemployment"],
    "jobs": ["youth_unemployment"],
    "cv": ["youth_unemployment"],
    "internship": ["youth_unemployment"],
    "graduate": ["youth_unemployment", "education"],
    "data": ["digital_divide", "privacy"],
    "wifi": ["digital_divide"],
    "internet": ["digital_divide"],
    "online": ["digital_divide"],
    "connectivity": ["digital_divide"],
    "taxi": ["taxi_industry"],
    "taxis": ["taxi_industry"],
    "minibus": ["taxi_industry"],
    "commute": ["taxi_industry"],
    "rank": ["taxi_industry"],
    "clinic": ["clinic_queues", "healthcare"],
    "hospital": ["clinic_queues", "healthcare"],
    "queue": ["clinic_queues", "sassa_grants"],
    "medication": ["clinic_queues", "healthcare"],
    "evict": ["evictions", "housing"],
    "eviction": ["evictions", "housing"],
    "evicted": ["evictions", "housing"],
    "landlord": ["evictions", "housing"],
    "shack": ["evictions", "housing"],
    "matric": ["matric_exams", "education"],
    "exams": ["matric_exams", "education"],
    "nsc": ["matric_exams"],
    "results": ["matric_exams"],
    "femicide": ["femicide", "gbv"],
    "killed": ["femicide", "gbv"],
    "murdered": ["femicide", "gbv"],
    "gbv": ["gbv", "femicide"],
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

    def get_trending_sa_topics(self) -> list[str]:
        """Get list of topics mapping to current SA discourse.

        These are topics that reflect real conversations happening
        in South African society - the things people argue about
        on Twitter, discuss at taxi ranks, and experience daily.

        Returns:
            List of trending SA topic names.
        """
        # These are the SA-specific trending topics that connect
        # to everyday South African experiences
        sa_trend_topics = [
            "sassa_grants",
            "nsfas",
            "municipality_failures",
            "youth_unemployment",
            "digital_divide",
            "taxi_industry",
            "clinic_queues",
            "evictions",
            "matric_exams",
            "femicide",
            "load shedding",
            "corruption",
            "xenophobia",
            "gbv",
            "police brutality",
            "housing",
            "water",
            "education",
        ]

        # Return only topics that exist in our mapping
        return [t for t in sa_trend_topics if t in self.topic_map]

    def get_random_sa_topic(self) -> Optional[str]:
        """Get a random SA trending topic for content generation.

        Returns:
            A random topic from SA trends, or None if none available.
        """
        import random
        topics = self.get_trending_sa_topics()
        return random.choice(topics) if topics else None
