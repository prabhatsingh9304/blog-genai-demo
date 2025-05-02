"use client";

import { BlogAgentWrapper } from "@/components/bloging/BlogAgent";
import { Header } from "@/components/layout/Header";
import GoogleTrendsWidget from "@/components/trend/GoogleTrendWidget";
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
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-4xl mx-auto">
          <BlogAgentWrapper />
        </div>
      </main>
      {/* <div>
        <GoogleTrendsWidget />
      </div> */}
    </div>
  );
}
