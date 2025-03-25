"use client";

import { StakingAgentWrapper } from "@/components/staking/StakingAgent";
import { Inter } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export default function Home() {
  return (
    <div
      className={`min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50 ${inter.variable} font-sans`}
    >
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-purple-500 bg-clip-text text-transparent">
              Blog Generator
            </h1>
            <p className="text-sm text-gray-500">Top-Trending Blog Generator</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-4xl mx-auto">
          <StakingAgentWrapper />
        </div>
      </main>
    </div>
  );
}
