import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SEO Blog Generator",
  description: "Optimize your staking rewards with AI-powered strategies",
  keywords: [
    "blog-generator",
    "ai-marketing",
    "content-generation",
    "marketing-tools",
    "trending blog",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
