import os
import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import tempfile

from data_loader import load_candidates, load_job_description
from jd_parser import parse_job_description, get_jd_embedding_text
from embeddings import precompute_embeddings, embed_jd, load_embeddings
from ranker import rank_candidates


app = FastAPI(title="Candidate Ranker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EMBEDDINGS_PATH = "./cache/candidate_embeddings.npy"


class RankRequest(BaseModel):
    jd_text: str
    top_k: Optional[int] = 100


class CandidateResult(BaseModel):
    rank: int
    candidate_id: str
    final_score: float
    semantic_score: float
    behavioral_score: float
    reasoning: str


class RankResponse(BaseModel):
    total_candidates: int
    ranked: List[CandidateResult]


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/rank", response_model=RankResponse)
async def rank_endpoint(request: RankRequest):
    candidates_path = os.environ.get("CANDIDATES_PATH", "../data/candidates.jsonl")

    if not os.path.exists(candidates_path):
        raise HTTPException(status_code=404, detail="Candidates dataset not found")

    df = load_candidates(candidates_path)
    parsed_jd = parse_job_description(request.jd_text)
    jd_text_for_embedding = get_jd_embedding_text(parsed_jd)

    if os.path.exists(EMBEDDINGS_PATH):
        candidate_embeddings = load_embeddings(EMBEDDINGS_PATH)
    else:
        candidate_embeddings = precompute_embeddings(df, EMBEDDINGS_PATH)

    jd_embedding = embed_jd(jd_text_for_embedding)
    ranked = rank_candidates(
        df,
        candidate_embeddings,
        jd_embedding,
        parsed_jd,
        top_k=request.top_k
    )

    return RankResponse(
        total_candidates=len(df),
        ranked=[CandidateResult(**r) for r in ranked]
    )


@app.post("/api/rank/upload")
async def rank_with_upload(
    candidates_file: UploadFile = File(...),
    jd_file: UploadFile = File(...)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as tmp_candidates:
        tmp_candidates.write(await candidates_file.read())
        candidates_path = tmp_candidates.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_jd:
        tmp_jd.write(await jd_file.read())
        jd_path = tmp_jd.name

    df = load_candidates(candidates_path)
    jd_text = load_job_description(jd_path)
    parsed_jd = parse_job_description(jd_text)
    jd_text_for_embedding = get_jd_embedding_text(parsed_jd)

    candidate_embeddings = precompute_embeddings(df, EMBEDDINGS_PATH)
    jd_embedding = embed_jd(jd_text_for_embedding)

    ranked = rank_candidates(
        df,
        candidate_embeddings,
        jd_embedding,
        parsed_jd,
        top_k=100
    )

    os.unlink(candidates_path)
    os.unlink(jd_path)

    return {"total_candidates": len(df), "ranked": ranked}