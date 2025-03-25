"use client";

import { useState, useEffect } from "react";
import { StakingService } from "@/services/staking";
import { ErrorBoundary } from "@/components/error/ErrorBoundary";
import { ApiError } from "@/components/error/ApiError";

interface Message {
  role: "user" | "assistant";
  content: string;
  data?: any;
}

export function StakingAgentWrapper() {
  return (
    <ErrorBoundary>
      <StakingAgent />
    </ErrorBoundary>
  );
}

function StakingAgent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const stakingService = new StakingService();

  // Initial greeting
  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content:
          "Hi! I'm your blog generation assistant. I will help you to generate top trending blog. Can you please tell me the topic for blog?",
      },
    ]);
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput("");
    setIsLoading(true);
    setError(null);

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);

    try {
      // Get response from agent
      const response = await stakingService.chat(userMessage);

      // Add agent response
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.message,
          data: response.data,
        },
      ]);
    } catch (error) {
      console.error("Error:", error);
      setError(
        "Failed to get response from blog generating agent. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-xl overflow-hidden border border-gray-100">
      {/* Chat Messages */}
      <div className="h-[600px] overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-gray-50 to-white">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            } animate-fade-in`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-6 py-4 shadow-sm ${
                message.role === "user"
                  ? "bg-purple-100 text-black"
                  : "bg-white border border-gray-100 text-black"
              }`}
            >
              <div className="whitespace-pre-wrap break-words text-[15px] leading-relaxed">
                {message.content.split("\n").map((line, i) => (
                  <div
                    key={i}
                    className={`${line.trim().startsWith("-") ? "pl-4" : ""}`}
                  >
                    {line}
                  </div>
                ))}
              </div>
              {message.data && (
                <div className="mt-3 pt-3 border-t border-gray-200 text-sm space-y-1 opacity-90">
                  {Object.entries(message.data).map(([key, value]) => (
                    <div key={key} className="flex gap-3">
                      <span className="font-medium capitalize">{key}:</span>
                      <span>{String(value)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start animate-fade-in">
            <div className="bg-white border border-gray-100 rounded-2xl px-6 py-4 text-gray-500 shadow-sm">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="px-6 py-4 bg-red-50">
          <ApiError message={error} onRetry={() => setError(null)} />
        </div>
      )}

      {/* Input Form */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-gray-100 bg-white p-6"
      >
        <div className="flex gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tell me about topic..."
            className="flex-1 rounded-xl border border-gray-200 px-6 py-3 text-[15px] text-black placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-shadow"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="bg-purple-600 text-white px-8 py-3 rounded-xl hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 font-medium transition-all"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}

export default StakingAgentWrapper;
