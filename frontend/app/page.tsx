"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const [jdText, setJdText] = useState("");
  const [topK, setTopK] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRank = async () => {
    if (!jdText.trim()) {
      setError("Please enter a job description.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/rank", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jd_text: jdText, top_k: topK }),
      });
      if (!response.ok) {
        throw new Error("Failed to rank candidates. Make sure the backend is running.");
      }
      const data = await response.json();
      sessionStorage.setItem("rankResults", JSON.stringify(data));
      router.push("/results");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-10">
        <h1 className="text-4xl font-bold text-white mb-3">
          Intelligent Candidate Ranker
        </h1>
        <p className="text-gray-400 text-lg">
          Paste a job description below. Our system ranks candidates by semantic
          fit, career signals, and platform activity — not just keywords.
        </p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Job Description
          </label>
          <textarea
            className="w-full h-64 bg-gray-950 border border-gray-700 rounded-xl px-4 py-3 text-gray-100 placeholder-gray-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-none text-sm leading-relaxed"
            placeholder="Paste the full job description here..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Number of candidates to return
          </label>
          <select
            className="bg-gray-950 border border-gray-700 rounded-xl px-4 py-2.5 text-gray-100 focus:outline-none focus:border-blue-500 text-sm"
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
          >
            <option value={10}>Top 10</option>
            <option value={25}>Top 25</option>
            <option value={50}>Top 50</option>
            <option value={100}>Top 100</option>
          </select>
        </div>

        {error && (
          <div className="bg-red-950 border border-red-800 text-red-300 rounded-xl px-4 py-3 text-sm">
            {error}
          </div>
        )}

        <button
          onClick={handleRank}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors text-sm"
        >
          {loading ? "Ranking candidates..." : "Rank Candidates"}
        </button>
      </div>

      <div className="mt-10 grid grid-cols-3 gap-4">
        {[
          {
            title: "Semantic Matching",
            desc: "Understands meaning, not just keywords",
          },
          {
            title: "Behavioral Signals",
            desc: "23 platform activity signals integrated",
          },
          {
            title: "Explainable Results",
            desc: "Every rank backed by real evidence",
          },
        ].map((item) => (
          <div
            key={item.title}
            className="bg-gray-900 border border-gray-800 rounded-xl p-4"
          >
            <h3 className="text-white font-medium text-sm mb-1">{item.title}</h3>
            <p className="text-gray-500 text-xs">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}