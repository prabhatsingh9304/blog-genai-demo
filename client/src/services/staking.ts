const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatResponse {
  message: string;
  success: boolean;
  error?: string;
  data?: any;
}

export class StakingService {
  async chat(message: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();
      return {
        message: data.message,
        success: data.success,
        error: data.error,
        data: data.data,
      };
    } catch (error) {
      console.error("Error in chat:", error);
      throw error;
    }
  }
}
