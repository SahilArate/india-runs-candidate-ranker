import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Candidate Ranker — India Runs",
  description: "AI-powered intelligent candidate ranking system",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-950 text-gray-100 min-h-screen`}>
        <nav className="border-b border-gray-800 bg-gray-900 px-6 py-4">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                CR
              </div>
              <Link href="/" className="font-semibold text-white text-lg hover:text-blue-400 transition-colors">
                CandidateRanker
              </Link>
              <span className="text-gray-500 text-sm hidden md:block">
                — Intelligent Hiring Intelligence
              </span>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-400">
              <Link href="/" className="hover:text-white transition-colors">
                Rank
              </Link>
              <a
                href="https://github.com/SahilArate/india-runs-candidate-ranker"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-white transition-colors"
              >
                GitHub
              </a>
            </div>
          </div>
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-10">{children}</main>
        <footer className="border-t border-gray-800 mt-20 px-6 py-6 text-center text-gray-600 text-sm">
          Built for India Runs — Data & AI Challenge
        </footer>
      </body>
    </html>
  );
}