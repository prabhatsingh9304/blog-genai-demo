const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatResponse {
  message: string;
  success: boolean;
  error?: string;
  data?: any;
}

export class BlogService {
  async chat(message: string, onChunk?: (chunk: string) => void): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          topic: message,
          randomness: 0.8
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      if (onChunk && response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedMessage = "";
        let previousChunk = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          try {
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (!line.trim()) continue;

              const jsonStr = line.replace(/^data: /, '').trim();
              if (!jsonStr) continue;

              const data = JSON.parse(jsonStr);

              if (data.chunk) {
                // Use the utility function to handle potential duplicates
                const newContent = removeDuplicateStart(previousChunk, data.chunk);
                if (newContent) {
                  accumulatedMessage += newContent;
                  onChunk(newContent);
                  previousChunk = data.chunk;
                }
              }
            }
          } catch (e) {
            console.error("[BlogService] Error parsing chunk:", e);
            console.error("[BlogService] Raw chunk that failed:", chunk);
            // Continue processing even if one chunk fails
            continue;
          }
        }

        return {
          message: accumulatedMessage,
          success: true,
        };
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

// Utility function to remove duplicates at the start of a chunk
function removeDuplicateStart(previousChunk: string, newChunk: string): string {
  // If the new chunk starts with a duplicate of the previous chunk, 
  // trim the duplicate part
  for (let i = Math.floor(newChunk.length / 2); i > 0; i--) {
    const potentialDuplicate = newChunk.slice(0, i);
    if (previousChunk.endsWith(potentialDuplicate)) {
      return newChunk.slice(i);
    }
  }
  
  return newChunk;
}
