import numpy as np
import pandas as pd
from typing import Dict
from datetime import datetime


def compute_recency_score(last_active_date: str) -> float:
    if not last_active_date:
        return 0.3
    try:
        last_active = datetime.strptime(str(last_active_date), "%Y-%m-%d")
        days_inactive = (datetime.now() - last_active).days
        if days_inactive <= 7:
            return 1.0
        if days_inactive <= 30:
            return 0.9
        if days_inactive <= 90:
            return 0.7
        if days_inactive <= 180:
            return 0.5
        if days_inactive <= 365:
            return 0.3
        return 0.1
    except Exception:
        return 0.3


def compute_response_rate_score(response_rate: float) -> float:
    if pd.isna(response_rate) or response_rate < 0:
        return 0.3
    return round(min(1.0, float(response_rate)), 4)


def compute_interview_completion_score(completion_rate: float) -> float:
    if pd.isna(completion_rate) or completion_rate < 0:
        return 0.3
    return round(min(1.0, float(completion_rate)), 4)


def compute_github_activity_score(github_score: float) -> float:
    if pd.isna(github_score) or github_score < 0:
        return 0.3
    return round(min(1.0, float(github_score) / 100.0), 4)


def compute_open_to_work_bonus(open_to_work: bool) -> float:
    return 1.1 if open_to_work else 1.0


def compute_profile_completeness_score(completeness: float) -> float:
    if pd.isna(completeness) or completeness < 0:
        return 0.3
    return round(min(1.0, float(completeness)), 4)


def compute_notice_period_modifier(notice_days: int, preferred_max: int = 30) -> float:
    if pd.isna(notice_days) or notice_days < 0:
        return 0.7
    if notice_days <= preferred_max:
        return 1.0
    if notice_days <= 60:
        return 0.85
    if notice_days <= 90:
        return 0.7
    return 0.5


def compute_behavioral_score(signals: Dict) -> float:
    recency = compute_recency_score(signals.get("last_active_date", ""))
    response_rate = compute_response_rate_score(signals.get("recruiter_response_rate", 0.5))
    interview_completion = compute_interview_completion_score(signals.get("interview_completion_rate", 0.5))
    github_activity = compute_github_activity_score(signals.get("github_activity_score", 0))
    profile_completeness = compute_profile_completeness_score(signals.get("profile_completeness", 0.5))
    notice_modifier = compute_notice_period_modifier(signals.get("notice_period_days", 30))
    open_to_work_bonus = compute_open_to_work_bonus(signals.get("open_to_work", False))

    weighted_score = (
        recency * 0.25 +
        response_rate * 0.25 +
        interview_completion * 0.20 +
        github_activity * 0.15 +
        profile_completeness * 0.15
    )

    final_score = weighted_score * notice_modifier * open_to_work_bonus
    return round(min(1.0, float(final_score)), 4)


def extract_signals(candidate: Dict) -> Dict:
    redrob_signals = candidate.get("redrob_signals", {})
    if not isinstance(redrob_signals, dict):
        redrob_signals = {}

    return {
        "last_active_date": redrob_signals.get("last_active_date", ""),
        "recruiter_response_rate": redrob_signals.get("recruiter_response_rate", 0.5),
        "interview_completion_rate": redrob_signals.get("interview_completion_rate", 0.5),
        "github_activity_score": redrob_signals.get("github_activity_score", 0),
        "profile_completeness": redrob_signals.get("profile_completeness", 0.5),
        "notice_period_days": candidate.get("notice_period_days", 30),
        "open_to_work": candidate.get("open_to_work", False)
    }