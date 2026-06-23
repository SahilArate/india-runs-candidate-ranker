import numpy as np
import pandas as pd
from typing import List, Dict
from feature_engineering import extract_features
from behavioral_scorer import compute_behavioral_score, extract_signals
from honeypot_filter import compute_honeypot_penalty
from embeddings import compute_semantic_scores
from reasoning_generator import generate_reasoning
from jd_parser import ParsedJD


def compute_final_score(
    semantic_score: float,
    features: Dict,
    behavioral_score: float,
    honeypot_penalty: float
) -> float:
    if honeypot_penalty == 0.0:
        return 0.0

    title_relevance = features["title_relevance"]
    if title_relevance == 0.0:
        return 0.0

    weighted_score = (
        semantic_score * 0.35 +
        title_relevance * 0.20 +
        features["experience_fit"] * 0.15 +
        features["company_type_score"] * 0.10 +
        features["location_score"] * 0.05 +
        features["notice_period_score"] * 0.05 +
        behavioral_score * 0.10
    )

    final = weighted_score * features["title_hopper_penalty"] * honeypot_penalty
    return round(float(final), 6)


def rank_candidates(
    df: pd.DataFrame,
    candidate_embeddings: np.ndarray,
    jd_embedding: np.ndarray,
    parsed_jd: ParsedJD,
    top_k: int = 100
) -> List[Dict]:
    semantic_scores = compute_semantic_scores(candidate_embeddings, jd_embedding)

    records = df.to_dict("records")
    results = []

    for idx, candidate in enumerate(records):
        semantic_score = float(semantic_scores[idx])
        features = extract_features(
            candidate,
            parsed_jd.min_experience_years,
            parsed_jd.max_experience_years,
            parsed_jd.locations
        )
        signals = extract_signals(candidate)
        behavioral_score = compute_behavioral_score(signals)
        honeypot_penalty = compute_honeypot_penalty(candidate)

        final_score = compute_final_score(
            semantic_score,
            features,
            behavioral_score,
            honeypot_penalty
        )

        results.append({
            "candidate_id": candidate.get("candidate_id", f"candidate_{idx}"),
            "final_score": final_score,
            "semantic_score": round(semantic_score, 6),
            "behavioral_score": behavioral_score,
            "honeypot_penalty": honeypot_penalty,
            "features": features,
            "candidate_data": candidate
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)
    top_results = results[:top_k]

    output = []
    for rank, result in enumerate(top_results, start=1):
        candidate = result["candidate_data"]
        reasoning = generate_reasoning(
            candidate,
            parsed_jd,
            result["final_score"],
            rank
        )
        output.append({
            "rank": rank,
            "candidate_id": result["candidate_id"],
            "final_score": result["final_score"],
            "semantic_score": result["semantic_score"],
            "behavioral_score": result["behavioral_score"],
            "reasoning": reasoning
        })

    return output