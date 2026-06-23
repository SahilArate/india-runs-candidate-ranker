import argparse
import os
import sys
import time
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from data_loader import load_candidates, load_job_description
from jd_parser import parse_job_description, get_jd_embedding_text
from embeddings import precompute_embeddings, embed_jd, load_embeddings
from ranker import rank_candidates


EMBEDDINGS_CACHE = "./cache/candidate_embeddings.npy"
DEFAULT_JD_PATH = "./data/job_description.txt"


def parse_args():
    parser = argparse.ArgumentParser(description="Rank candidates against a job description")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--jd", default=DEFAULT_JD_PATH, help="Path to job description file")
    parser.add_argument("--out", required=True, help="Path to output CSV file")
    parser.add_argument("--top_k", type=int, default=100, help="Number of top candidates to return")
    parser.add_argument("--recompute", action="store_true", help="Force recompute embeddings")
    return parser.parse_args()


def build_output_dataframe(ranked_results: list) -> pd.DataFrame:
    rows = []
    for result in ranked_results:
        rows.append({
            "rank": result["rank"],
            "candidate_id": result["candidate_id"],
            "final_score": result["final_score"],
            "semantic_score": result["semantic_score"],
            "behavioral_score": result["behavioral_score"],
            "reasoning": result["reasoning"]
        })
    return pd.DataFrame(rows)


def main():
    args = parse_args()
    start_time = time.time()

    print(f"Loading candidates from {args.candidates}...")
    df = load_candidates(args.candidates)
    print(f"Loaded {len(df)} candidates")

    print(f"Parsing job description from {args.jd}...")
    jd_text = load_job_description(args.jd)
    parsed_jd = parse_job_description(jd_text)
    jd_embedding_text = get_jd_embedding_text(parsed_jd)

    os.makedirs("./cache", exist_ok=True)

    if os.path.exists(EMBEDDINGS_CACHE) and not args.recompute:
        print("Loading cached embeddings...")
        candidate_embeddings = load_embeddings(EMBEDDINGS_CACHE)
    else:
        print("Computing candidate embeddings (this runs once and is cached)...")
        candidate_embeddings = precompute_embeddings(df, EMBEDDINGS_CACHE)

    print("Embedding job description...")
    jd_embedding = embed_jd(jd_embedding_text)

    print(f"Ranking {len(df)} candidates...")
    ranking_start = time.time()
    ranked = rank_candidates(df, candidate_embeddings, jd_embedding, parsed_jd, top_k=args.top_k)
    ranking_time = time.time() - ranking_start

    os.makedirs(os.path.dirname(args.out) if os.path.dirname(args.out) else ".", exist_ok=True)
    output_df = build_output_dataframe(ranked)
    output_df.to_csv(args.out, index=False)

    total_time = time.time() - start_time
    print(f"\nDone.")
    print(f"Ranking step completed in {round(ranking_time, 2)}s")
    print(f"Total runtime: {round(total_time, 2)}s")
    print(f"Output saved to {args.out}")
    print(f"\nTop 5 candidates:")
    print(output_df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()