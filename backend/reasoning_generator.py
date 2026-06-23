from typing import Dict
from jd_parser import ParsedJD


def generate_reasoning(candidate: Dict, parsed_jd: ParsedJD, final_score: float, rank: int) -> str:
    parts = []

    title = candidate.get("current_title", "Unknown Title")
    years = candidate.get("years_of_experience", 0)
    location = candidate.get("location", "Unknown Location")

    parts.append(f"Ranked #{rank} with an overall fit score of {round(final_score, 3)}.")
    parts.append(f"{title} with {years} years of experience based in {location}.")

    skills = candidate.get("skills", [])
    if isinstance(skills, list) and skills:
        skill_names = []
        for s in skills:
            if isinstance(s, dict):
                skill_names.append(s.get("name", ""))
            elif isinstance(s, str):
                skill_names.append(s)
        matched = [
            s for s in skill_names
            if any(req.lower() in s.lower() for req in parsed_jd.must_have_skills)
        ]
        if matched:
            parts.append(f"Matched core requirements: {', '.join(matched[:5])}.")

    career = candidate.get("career_history", [])
    if isinstance(career, list) and career:
        recent = career[0]
        if isinstance(recent, dict):
            company = recent.get("company_name", "")
            role = recent.get("title", "")
            if company and role:
                parts.append(f"Most recent role: {role} at {company}.")

    redrob_signals = candidate.get("redrob_signals", {})
    if isinstance(redrob_signals, dict):
        response_rate = redrob_signals.get("recruiter_response_rate", None)
        if response_rate is not None:
            rate_pct = round(float(response_rate) * 100)
            if rate_pct >= 70:
                parts.append(f"High recruiter responsiveness at {rate_pct}%.")
            elif rate_pct < 40:
                parts.append(f"Note: recruiter response rate is low at {rate_pct}%.")

        last_active = redrob_signals.get("last_active_date", None)
        if last_active:
            parts.append(f"Last active on platform: {last_active}.")

    notice_days = candidate.get("notice_period_days", None)
    if notice_days is not None:
        if notice_days <= 30:
            parts.append(f"Available within {notice_days} days — fits immediate hiring need.")
        else:
            parts.append(f"Notice period is {notice_days} days.")

    open_to_work = candidate.get("open_to_work", False)
    if open_to_work:
        parts.append("Actively open to new opportunities.")

    if years < parsed_jd.min_experience_years:
        gap = parsed_jd.min_experience_years - years
        parts.append(f"Concern: {gap} year(s) below minimum experience requirement.")
    elif years > parsed_jd.max_experience_years + 3:
        parts.append("Note: significantly over-experienced for this role level.")

    return " ".join(parts)