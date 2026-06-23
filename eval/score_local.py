import pandas as pd
import numpy as np
import argparse
from typing import List


def compute_dcg(relevances: List[float], k: int) -> float:
    relevances = relevances[:k]
    if not relevances:
        return 0.0
    positions = np.arange(1, len(relevances) + 1)
    gains = np.array(relevances) / np.log2(positions + 1)
    return float(np.sum(gains))


def compute_ndcg(ranked_ids: List[str], gold: dict, k: int) -> float:
    relevances = [gold.get(cid, 0) for cid in ranked_ids[:k]]
    dcg = compute_dcg(relevances, k)
    ideal = sorted(gold.values(), reverse=True)
    idcg = compute_dcg(ideal, k)
    if idcg == 0:
        return 0.0
    return round(dcg / idcg, 4)


def compute_map(ranked_ids: List[str], gold: dict) -> float:
    relevant_found = 0
    precision_sum = 0.0
    for i, cid in enumerate(ranked_ids, start=1):
        if gold.get(cid, 0) > 0:
            relevant_found += 1
            precision_sum += relevant_found / i
    total_relevant = sum(1 for v in gold.values() if v > 0)
    if total_relevant == 0:
        return 0.0
    return round(precision_sum / total_relevant, 4)


def compute_precision_at_k(ranked_ids: List[str], gold: dict, k: int) -> float:
    top_k = ranked_ids[:k]
    relevant = sum(1 for cid in top_k if gold.get(cid, 0) > 0)
    return round(relevant / k, 4)


def compute_final_score(ndcg10: float, ndcg50: float, map_score: float, p10: float) -> float:
    return round(0.50 * ndcg10 + 0.30 * ndcg50 + 0.15 * map_score + 0.05 * p10, 4)


def load_gold_set(path: str) -> dict:
    df = pd.read_csv(path)
    return dict(zip(df["candidate_id"], df["relevance_score"]))


def load_submission(path: str) -> List[str]:
    df = pd.read_csv(path)
    df = df.sort_values("rank")
    return df["candidate_id"].tolist()


def main():
    parser = argparse.ArgumentParser(description="Score your submission locally against gold set")
    parser.add_argument("--submission", required=True, help="Path to your submission CSV")
    parser.add_argument("--gold", required=True, help="Path to gold set CSV")
    args = parser.parse_args()

    gold = load_gold_set(args.gold)
    ranked_ids = load_submission(args.submission)

    ndcg10 = compute_ndcg(ranked_ids, gold, k=10)
    ndcg50 = compute_ndcg(ranked_ids, gold, k=50)
    map_score = compute_map(ranked_ids, gold)
    p10 = compute_precision_at_k(ranked_ids, gold, k=10)
    final = compute_final_score(ndcg10, ndcg50, map_score, p10)

    print("\n========== LOCAL EVALUATION RESULTS ==========")
    print(f"NDCG@10  (weight 0.50) : {ndcg10}")
    print(f"NDCG@50  (weight 0.30) : {ndcg50}")
    print(f"MAP      (weight 0.15) : {map_score}")
    print(f"P@10     (weight 0.05) : {p10}")
    print(f"----------------------------------------------")
    print(f"FINAL SCORE            : {final}")
    print("==============================================\n")


if __name__ == "__main__":
    main()