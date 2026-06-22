import numpy as np
import joblib
import os
from sentence_transformers import SentenceTransformer
from typing import List
import pandas as pd


MODEL_NAME = "all-MiniLM-L6-v2"
CACHE_DIR = "./cache"


def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def build_candidate_text(candidate: dict) -> str:
    parts = []
    
    if candidate.get("current_title"):
        parts.append(candidate["current_title"])
    
    if candidate.get("headline"):
        parts.append(candidate["headline"])
    
    if candidate.get("summary"):
        parts.append(candidate["summary"])
    
    skills = candidate.get("skills", [])
    if isinstance(skills, list) and skills:
        skill_names = []
        for s in skills:
            if isinstance(s, dict):
                skill_names.append(s.get("name", ""))
            elif isinstance(s, str):
                skill_names.append(s)
        parts.append("Skills: " + ", ".join(filter(None, skill_names)))
    
    career = candidate.get("career_history", [])
    if isinstance(career, list):
        for role in career[:3]:
            if isinstance(role, dict):
                role_text = f"{role.get('title', '')} at {role.get('company_name', '')}"
                if role.get("description"):
                    role_text += f": {role['description'][:200]}"
                parts.append(role_text)
    
    return " | ".join(filter(None, parts))


def precompute_embeddings(df: pd.DataFrame, output_path: str) -> np.ndarray:
    os.makedirs(CACHE_DIR, exist_ok=True)
    model = get_model()
    
    texts = [build_candidate_text(row) for row in df.to_dict("records")]
    
    print(f"Computing embeddings for {len(texts)} candidates...")
    embeddings = model.encode(
        texts,
        batch_size=256,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    
    np.save(output_path, embeddings)
    print(f"Embeddings saved to {output_path}")
    return embeddings


def load_embeddings(path: str) -> np.ndarray:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Embeddings not found at {path}. Run precompute first.")
    return np.load(path)


def embed_jd(jd_text: str) -> np.ndarray:
    model = get_model()
    embedding = model.encode(
        [jd_text],
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    return embedding[0]


def compute_semantic_scores(candidate_embeddings: np.ndarray, jd_embedding: np.ndarray) -> np.ndarray:
    scores = candidate_embeddings @ jd_embedding
    return scores.astype(np.float32)