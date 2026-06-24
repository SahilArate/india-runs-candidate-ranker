"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface CandidateResult {
  rank: number;
  candidate_id: string;
  final_score: number;
  semantic_score: number;
  behavioral_score: number;
  reasoning: string;
}

interface RankResponse {
  total_candidates: number;
  ranked: CandidateResult[];
}

function ScoreBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 75
      ? "bg-green-900 text-green-300 border-green-800"
      : pct >= 50
      ? "bg-blue-900 text-blue-300 border-blue-800"
      : pct >= 30
      ? "bg-yellow-900 text-yellow-300 border-yellow-800"
      : "bg-red-900 text-red-300 border-red-800";
  return (
    <span className={`border text-xs font-semibold px-2 py-0.5 rounded-full ${color}`}>
      {pct}%
    </span>
  );
}

function ScoreBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="w-full bg-gray-800 rounded-full h-1.5">
      <div
        className={`h-1.5 rounded-full ${color}`}
        style={{ width: `${Math.round(value * 100)}%` }}
      />
    </div>
  );
}

export default function ResultsPage() {
  const router = useRouter();
  const [data, setData] = useState<RankResponse | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const stored = sessionStorage.getItem("rankResults");
    if (!stored) {
      router.push("/");
      return;
    }
    setData(JSON.parse(stored));
  }, [router]);

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        Loading results...
      </div>
    );
  }

  const filtered = data.ranked.filter((c) =>
    search.trim()
      ? c.candidate_id.toLowerCase().includes(search.toLowerCase()) ||
        c.reasoning.toLowerCase().includes(search.toLowerCase())
      : true
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-1">Ranked Shortlist</h1>
          <p className="text-gray-400 text-sm">
            Top {data.ranked.length} candidates from a pool of{" "}
            {data.total_candidates.toLocaleString()} profiles
          </p>
        </div>
        <Link
          href="/"
          className="text-sm text-gray-400 hover:text-white transition-colors border border-gray-700 rounded-xl px-4 py-2"
        >
          ← New Search
        </Link>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          {
            label: "Total Candidates",
            value: data.total_candidates.toLocaleString(),
          },
          {
            label: "Shortlisted",
            value: data.ranked.length,
          },
          {
            label: "Top Score",
            value: `${Math.round(data.ranked[0]?.final_score * 100)}%`,
          },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-gray-900 border border-gray-800 rounded-xl p-4"
          >
            <p className="text-gray-500 text-xs mb-1">{stat.label}</p>
            <p className="text-white text-2xl font-bold">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Search by candidate ID or reasoning..."
          className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-2.5 text-gray-100 placeholder-gray-600 focus:outline-none focus:border-blue-500 text-sm"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="space-y-3">
        {filtered.map((candidate) => (
          <div
            key={candidate.candidate_id}
            className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden"
          >
            <button
              className="w-full text-left px-6 py-4 flex items-center justify-between hover:bg-gray-800 transition-colors"
              onClick={() =>
                setExpanded(
                  expanded === candidate.candidate_id
                    ? null
                    : candidate.candidate_id
                )
              }
            >
              <div className="flex items-center gap-4">
                <span className="text-gray-600 text-sm font-mono w-8">
                  #{candidate.rank}
                </span>
                <div>
                  <p className="text-white font-medium text-sm">
                    {candidate.candidate_id}
                  </p>
                  <p className="text-gray-500 text-xs mt-0.5 line-clamp-1 max-w-xl">
                    {candidate.reasoning}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <ScoreBadge score={candidate.final_score} />
                <span className="text-gray-600 text-xs">
                  {expanded === candidate.candidate_id ? "▲" : "▼"}
                </span>
              </div>
            </button>

            {expanded === candidate.candidate_id && (
              <div className="px-6 pb-5 border-t border-gray-800 pt-4 space-y-4">
                <p className="text-gray-300 text-sm leading-relaxed">
                  {candidate.reasoning}
                </p>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-gray-500 text-xs mb-1">Final Score</p>
                    <ScoreBar value={candidate.final_score} color="bg-blue-500" />
                    <p className="text-gray-300 text-xs mt-1">
                      {Math.round(candidate.final_score * 100)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 text-xs mb-1">Semantic Match</p>
                    <ScoreBar value={candidate.semantic_score} color="bg-purple-500" />
                    <p className="text-gray-300 text-xs mt-1">
                      {Math.round(candidate.semantic_score * 100)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500 text-xs mb-1">Behavioral Score</p>
                    <ScoreBar value={candidate.behavioral_score} color="bg-green-500" />
                    <p className="text-gray-300 text-xs mt-1">
                      {Math.round(candidate.behavioral_score * 100)}%
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center text-gray-600 py-20">
          No candidates match your search.
        </div>
      )}
    </div>
  );
}