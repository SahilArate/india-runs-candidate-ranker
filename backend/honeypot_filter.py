import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime


KNOWN_YOUNG_COMPANIES = {
    "openai": 2015,
    "anthropic": 2021,
    "mistral": 2023,
    "perplexity": 2022,
    "cohere": 2019,
    "hugging face": 2016,
    "groq": 2016,
    "together ai": 2022,
    "replicate": 2019,
    "langchain": 2022
}


def check_experience_consistency(candidate: Dict) -> float:
    years = candidate.get("years_of_experience", 0)
    career_history = candidate.get("career_history", [])

    if not isinstance(career_history, list) or len(career_history) == 0:
        return 1.0

    total_months = sum(
        role.get("duration_months", 0)
        for role in career_history
        if isinstance(role.get("duration_months"), (int, float))
    )

    claimed_months = years * 12

    if claimed_months > 0:
        ratio = total_months / claimed_months
        if ratio > 2.5 or ratio < 0.2:
            return 0.0

    return 1.0


def check_company_founding_consistency(candidate: Dict) -> float:
    career_history = candidate.get("career_history", [])

    if not isinstance(career_history, list):
        return 1.0

    for role in career_history:
        company = str(role.get("company_name", "")).lower().strip()
        duration = role.get("duration_months", 0)

        for company_name, founding_year in KNOWN_YOUNG_COMPANIES.items():
            if company_name in company:
                company_age_months = (datetime.now().year - founding_year) * 12
                if isinstance(duration, (int, float)) and duration > company_age_months:
                    return 0.0

    return 1.0


def check_skill_proficiency_consistency(candidate: Dict) -> float:
    skills = candidate.get("skills", [])

    if not isinstance(skills, list) or len(skills) == 0:
        return 1.0

    suspicious_count = 0
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        proficiency = str(skill.get("proficiency", "")).lower()
        duration = skill.get("duration_months", 12)

        if proficiency == "expert" and isinstance(duration, (int, float)) and duration < 6:
            suspicious_count += 1

    if len(skills) > 0 and suspicious_count / len(skills) > 0.5:
        return 0.0

    return 1.0


def check_skill_count_anomaly(candidate: Dict) -> float:
    skills = candidate.get("skills", [])

    if not isinstance(skills, list):
        return 1.0

    if len(skills) > 60:
        return 0.2

    if len(skills) > 40:
        return 0.6

    return 1.0


def check_profile_completeness(candidate: Dict) -> float:
    required_fields = [
        "candidate_id", "current_title", "years_of_experience",
        "skills", "career_history", "location"
    ]
    missing = sum(1 for f in required_fields if not candidate.get(f))
    if missing >= 4:
        return 0.0
    if missing >= 2:
        return 0.5
    return 1.0


def compute_honeypot_penalty(candidate: Dict) -> float:
    checks = [
        check_experience_consistency(candidate),
        check_company_founding_consistency(candidate),
        check_skill_proficiency_consistency(candidate),
        check_skill_count_anomaly(candidate),
        check_profile_completeness(candidate)
    ]

    if 0.0 in checks:
        return 0.0

    penalty = np.mean(checks)
    return round(float(penalty), 4)


def is_honeypot(candidate: Dict, threshold: float = 0.3) -> bool:
    return compute_honeypot_penalty(candidate) <= threshold