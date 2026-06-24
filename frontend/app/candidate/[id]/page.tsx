"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

interface CandidateResult {
  rank: number;
  candidate_id: string;
  final_score: number;
  semantic_score: number;
  behavioral_score: number;
  reasoning: string;
}

function ScoreRing({ value, label, color }: { value: number; label: string; color: string }) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex flex-col items-center gap-2">
      <div className={`w-20 h-20 rounded-full border-4 ${color} flex items-center justify-center`}>
        <span className="text-white font-bold text-lg">{pct}%</span>
      </div>
      <span className="text-gray-400 text-xs">{label}</span>
    </div>
  );
}

function ScoreBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="w-full bg-gray-800 rounded-full h-2">
      <div
        className={`h-2 rounded-full ${color} transition-all duration-500`}
        style={{ width: `${Math.round(value * 100)}%` }}
      />
    </div>
  );
}

export default function CandidateDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [candidate, setCandidate] = useState<CandidateResult | null>(null);
  const [allResults, setAllResults] = useState<CandidateResult[]>([]);

  useEffect(() => {
    const stored = sessionStorage.getItem("rankResults");
    if (!stored) {
      router.push("/");
      return;
    }
    const data = JSON.parse(stored);
    const all: CandidateResult[] = data.ranked;
    setAllResults(all);
    const found = all.find((c) => c.candidate_id === params.id);
    if (!found) {
      router.push("/results");
      return;
    }
    setCandidate(found);
  }, [params.id, router]);

  if (!candidate) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        Loading candidate...
      </div>
    );
  }

  const percentile = Math.round(
    ((allResults.length - candidate.rank) / allResults.length) * 100
  );

  const scoreBreakdown = [
    { label: "Final Score", value: candidate.final_score, color: "bg-blue-500" },
    { label: "Semantic Match", value: candidate.semantic_score, color: "bg-purple-500" },
    { label: "Behavioral Score", value: candidate.behavioral_score, color: "bg-green-500" },
  ];

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <Link
          href="/results"
          className="text-sm text-gray-400 hover:text-white transition-colors border border-gray-700 rounded-xl px-4 py-2"
        >
          ← Back to Results
        </Link>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                Rank #{candidate.rank}
              </span>
              <span className="bg-gray-800 text-gray-300 text-xs px-3 py-1 rounded-full">
                Top {100 - percentile}%
              </span>
            </div>
            <h1 className="text-2xl font-bold text-white">
              {candidate.candidate_id}
            </h1>
          </div>
          <div className="text-right">
            <p className="text-gray-500 text-xs mb-1">Overall Fit</p>
            <p className="text-4xl font-bold text-blue-400">
              {Math.round(candidate.final_score * 100)}%
            </p>
          </div>
        </div>

        <div className="flex justify-around py-4 border-t border-b border-gray-800 mb-6">
          <ScoreRing
            value={candidate.final_score}
            label="Final Score"
            color="border-blue-500"
          />
          <ScoreRing
            value={candidate.semantic_score}
            label="Semantic"
            color="border-purple-500"
          />
          <ScoreRing
            value={candidate.behavioral_score}
            label="Behavioral"
            color="border-green-500"
          />
        </div>

        <div className="space-y-4">
          {scoreBreakdown.map((item) => (
            <div key={item.label}>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-gray-400">{item.label}</span>
                <span className="text-gray-300 font-medium">
                  {Math.round(item.value * 100)}%
                </span>
              </div>
              <ScoreBar value={item.value} color={item.color} />
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6">
        <h2 className="text-white font-semibold mb-3">Why this candidate ranks here</h2>
        <p className="text-gray-300 text-sm leading-relaxed">{candidate.reasoning}</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
        <h2 className="text-white font-semibold mb-4">Nearby candidates</h2>
        <div className="space-y-2">
          {allResults
            .filter(
              (c) =>
                c.rank >= Math.max(1, candidate.rank - 2) &&
                c.rank <= candidate.rank + 2 &&
                c.candidate_id !== candidate.candidate_id
            )
            .map((c) => (
              <Link
                key={c.candidate_id}
                href={`/candidate/${c.candidate_id}`}
                className="flex items-center justify-between bg-gray-800 hover:bg-gray-700 rounded-xl px-4 py-3 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-gray-500 text-xs font-mono w-6">
                    #{c.rank}
                  </span>
                  <span className="text-gray-300 text-sm">{c.candidate_id}</span>
                </div>
                <span className="text-gray-400 text-xs">
                  {Math.round(c.final_score * 100)}%
                </span>
              </Link>
            ))}
        </div>
      </div>
    </div>
  );
}