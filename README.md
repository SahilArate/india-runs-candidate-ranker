# India Runs — Intelligent Candidate Ranker

A hybrid AI ranking system that scores and ranks candidates against a job description the way a great recruiter would — not by matching keywords, but by understanding who genuinely fits the role.

## How it works

The system combines three layers of intelligence:

1. **Semantic understanding** — converts candidate profiles and job descriptions into vector embeddings using a local pre-trained model, enabling semantic similarity matching beyond keyword overlap
2. **Feature engineering** — extracts structured signals from each candidate: title relevance, experience fit, career trajectory, company type, location, and notice period
3. **Behavioral signal fusion** — integrates 23 platform activity signals (recruiter response rate, last active date, GitHub activity, interview completion rate, profile completeness) as a weighted modifier on the base score

## Project structure
india-runs-candidate-ranker/

├── rank.py                        # Entry point — run this to produce submission.csv

├── submission_metadata.yaml       # Submission metadata and reproduce instructions

├── backend/

│   ├── data_loader.py             # Loads candidates.jsonl and job description

│   ├── jd_parser.py               # Parses JD into structured requirement schema

│   ├── embeddings.py              # Precomputes and caches candidate embeddings

│   ├── feature_engineering.py     # Extracts structured features per candidate

│   ├── behavioral_scorer.py       # Scores behavioral signals from redrob platform

│   ├── honeypot_filter.py         # Detects and penalizes inconsistent profiles

│   ├── ranker.py                  # Core ranking pipeline — fuses all signals

│   ├── reasoning_generator.py     # Generates field-grounded reasoning per candidate

│   ├── main.py                    # FastAPI server for frontend integration

│   └── requirements.txt           # Python dependencies

├── frontend/                      # Next.js recruiter dashboard

├── eval/

│   ├── score_local.py             # Local NDCG/MAP evaluation against gold set

│   └── gold_set.csv               # Hand-labeled candidates for local evaluation

└── data/

└── job_description.txt        # Job description used for ranking

## Setup

```bash
git clone https://github.com/SahilArate/india-runs-candidate-ranker.git
cd india-runs-candidate-ranker
pip install -r backend/requirements.txt
```

## Reproduce submission

```bash
python rank.py --candidates ./data/candidates.jsonl --jd ./data/job_description.txt --out ./submission.csv
```

The ranking step runs fully offline — no internet connection, no GPU, no external API calls required. Runtime is under 5 minutes on standard CPU hardware.

## Evaluate locally

```bash
python eval/score_local.py --submission ./submission.csv --gold ./eval/gold_set.csv
```

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| Embeddings | sentence-transformers all-MiniLM-L6-v2 | CPU-friendly, offline, strong semantic understanding |
| Vectorized scoring | numpy / pandas | Fast enough for 100K candidates within 5-min budget |
| Fuzzy matching | rapidfuzz | Robust title and skill normalization |
| API server | FastAPI + uvicorn | Async, fast, clean REST API |
| Frontend | Next.js + Tailwind CSS | Modern, responsive recruiter dashboard |
| Caching | joblib / numpy .npy | Precomputed embeddings avoid recomputation cost |

## Compute constraints

- CPU only — no GPU required
- No network calls during ranking
- Memory usage under 16GB
- Total ranking runtime under 5 minutes for 100,000 candidates