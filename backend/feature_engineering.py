import re
import pandas as pd
import numpy as np
from rapidfuzz import fuzz
from typing import Dict


PRODUCT_COMPANY_SIGNALS = [
    "google", "meta", "microsoft", "amazon", "apple", "netflix",
    "flipkart", "swiggy", "zomato", "razorpay", "cred", "meesho",
    "phonepe", "paytm", "freshworks", "zoho", "cleartax", "groww",
    "zerodha", "unacademy", "byju", "ola", "uber", "stripe",
    "airbnb", "linkedin", "twitter", "openai", "anthropic", "cohere",
    "huggingface", "databricks", "snowflake", "confluent", "notion"
]

IT_SERVICES_SIGNALS = [
    "tcs", "infosys", "wipro", "hcl", "tech mahindra", "cognizant",
    "capgemini", "accenture", "ibm", "mphasis", "hexaware", "ltimindtree",
    "persistent", "niit", "mindtree"
]

RELEVANT_TITLE_KEYWORDS = [
    "machine learning", "ml engineer", "ai engineer", "data scientist",
    "nlp engineer", "research engineer", "applied scientist",
    "deep learning", "computer vision", "ranking engineer",
    "search engineer", "recommendation", "applied ml"
]

DISQUALIFYING_TITLES = [
    "marketing manager", "hr manager", "sales manager", "product manager",
    "business analyst", "scrum master", "project manager", "account manager",
    "operations manager", "content writer", "seo specialist"
]


def compute_title_relevance_score(title: str) -> float:
    if not isinstance(title, str) or not title.strip():
        return 0.0
    title_lower = title.lower()
    for disqualifier in DISQUALIFYING_TITLES:
        if fuzz.partial_ratio(disqualifier, title_lower) > 85:
            return 0.0
    best_score = 0.0
    for keyword in RELEVANT_TITLE_KEYWORDS:
        score = fuzz.partial_ratio(keyword, title_lower) / 100.0
        best_score = max(best_score, score)
    return round(best_score, 4)


def compute_experience_fit_score(years: float, min_exp: int, max_exp: int) -> float:
    if pd.isna(years) or years < 0:
        return 0.0
    if min_exp <= years <= max_exp:
        return 1.0
    if years < min_exp:
        gap = min_exp - years
        return round(max(0.0, 1.0 - (gap * 0.15)), 4)
    if years > max_exp:
        excess = years - max_exp
        return round(max(0.5, 1.0 - (excess * 0.08)), 4)
    return 0.0


def compute_company_type_score(career_history: list) -> float:
    if not isinstance(career_history, list) or len(career_history) == 0:
        return 0.3
    product_count = 0
    services_count = 0
    for role in career_history:
        company = str(role.get("company_name", "")).lower()
        for pc in PRODUCT_COMPANY_SIGNALS:
            if pc in company:
                product_count += 1
                break
        for sc in IT_SERVICES_SIGNALS:
            if sc in company:
                services_count += 1
                break
    total = product_count + services_count
    if total == 0:
        return 0.5
    ratio = product_count / total
    return round(0.4 + (ratio * 0.6), 4)


def compute_title_hopper_penalty(career_history: list) -> float:
    if not isinstance(career_history, list) or len(career_history) < 3:
        return 1.0
    short_tenures = 0
    for role in career_history:
        duration = role.get("duration_months", 24)
        if isinstance(duration, (int, float)) and duration < 18:
            short_tenures += 1
    ratio = short_tenures / len(career_history)
    if ratio >= 0.6:
        return 0.4
    if ratio >= 0.4:
        return 0.7
    return 1.0


def compute_location_score(location: str, preferred_locations: list) -> float:
    if not isinstance(location, str) or not location.strip():
        return 0.5
    location_lower = location.lower()
    for preferred in preferred_locations:
        if preferred.lower() in location_lower:
            return 1.0
    return 0.6


def compute_notice_period_score(notice_days: int, max_preferred: int = 30) -> float:
    if pd.isna(notice_days) or notice_days < 0:
        return 0.5
    if notice_days <= max_preferred:
        return 1.0
    if notice_days <= 60:
        return 0.75
    if notice_days <= 90:
        return 0.5
    return 0.25


def extract_features(candidate: Dict, min_exp: int, max_exp: int, preferred_locations: list) -> Dict:
    career_history = candidate.get("career_history", [])
    return {
        "title_relevance": compute_title_relevance_score(
            candidate.get("current_title", "")
        ),
        "experience_fit": compute_experience_fit_score(
            candidate.get("years_of_experience", 0), min_exp, max_exp
        ),
        "company_type_score": compute_company_type_score(career_history),
        "title_hopper_penalty": compute_title_hopper_penalty(career_history),
        "location_score": compute_location_score(
            candidate.get("location", ""), preferred_locations
        ),
        "notice_period_score": compute_notice_period_score(
            candidate.get("notice_period_days", 30)
        )
    }