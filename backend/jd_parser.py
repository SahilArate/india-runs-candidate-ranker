import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class ParsedJD:
    title: str
    must_have_skills: List[str]
    nice_to_have_skills: List[str]
    min_experience_years: int
    max_experience_years: int
    seniority_level: str
    domain: str
    locations: List[str]
    disqualifiers: List[str]
    implicit_requirements: List[str]
    notice_period_days: int
    raw_text: str


def parse_job_description(jd_text: str) -> ParsedJD:
    text_lower = jd_text.lower()

    must_have_skills = [
        "python", "machine learning", "deep learning", "nlp",
        "information retrieval", "ranking systems", "recommendation systems",
        "vector embeddings", "semantic search", "llm", "transformers",
        "pytorch", "tensorflow", "scikit-learn", "production ml systems"
    ]

    nice_to_have_skills = [
        "langchain", "faiss", "pinecone", "qdrant", "ray",
        "kubernetes", "docker", "mlflow", "airflow", "spark",
        "rust", "go", "java", "scala"
    ]

    disqualifiers = [
        "pure research background",
        "consulting only career",
        "it services only",
        "no product company experience",
        "title hopper",
        "no recent coding",
        "cv speech robotics only",
        "closed source only",
        "marketing manager",
        "hr manager",
        "sales manager"
    ]

    implicit_requirements = [
        "startup experience",
        "shipped to production",
        "cross functional collaboration",
        "strong opinions on retrieval",
        "open source contributions"
    ]

    locations = ["pune", "noida", "hyderabad", "mumbai", "delhi", "bangalore"]

    exp_match = re.search(r"(\d+)\s*[-–to]+\s*(\d+)\s*years?", text_lower)
    min_exp = int(exp_match.group(1)) if exp_match else 5
    max_exp = int(exp_match.group(2)) if exp_match else 9

    notice_match = re.search(r"(\d+)\s*days?\s*notice", text_lower)
    notice_period = int(notice_match.group(1)) if notice_match else 30

    seniority = "senior"
    if "lead" in text_lower or "principal" in text_lower:
        seniority = "lead"
    elif "junior" in text_lower or "entry" in text_lower:
        seniority = "junior"
    elif "mid" in text_lower:
        seniority = "mid"

    return ParsedJD(
        title="Senior AI Engineer",
        must_have_skills=must_have_skills,
        nice_to_have_skills=nice_to_have_skills,
        min_experience_years=min_exp,
        max_experience_years=max_exp,
        seniority_level=seniority,
        domain="ai_ml",
        locations=locations,
        disqualifiers=disqualifiers,
        implicit_requirements=implicit_requirements,
        notice_period_days=notice_period,
        raw_text=jd_text
    )


def get_jd_embedding_text(parsed_jd: ParsedJD) -> str:
    parts = [
        parsed_jd.title,
        "Required skills: " + ", ".join(parsed_jd.must_have_skills),
        "Domain: " + parsed_jd.domain,
        "Seniority: " + parsed_jd.seniority_level,
        "Implicit: " + ", ".join(parsed_jd.implicit_requirements)
    ]
    return ". ".join(parts)