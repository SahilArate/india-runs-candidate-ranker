import json
import pandas as pd
from pathlib import Path


def load_candidates(filepath: str) -> pd.DataFrame:
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return pd.DataFrame(records)


def load_job_description(filepath: str) -> str:
    path = Path(filepath)
    if path.suffix == ".txt":
        return path.read_text(encoding="utf-8")
    if path.suffix == ".docx":
        from docx import Document
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    raise ValueError(f"Unsupported file type: {path.suffix}")


def get_candidate_by_id(df: pd.DataFrame, candidate_id: str) -> dict:
    result = df[df["candidate_id"] == candidate_id]
    if result.empty:
        raise ValueError(f"Candidate {candidate_id} not found")
    return result.iloc[0].to_dict()