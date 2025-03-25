const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      return {
        message: data.message,
        success: data.success,
        error: data.error,
        data: data.data
      };
    } catch (error) {
      console.error('Error in chat:', error);
      throw error;
    }
  }

  async getRewards(address: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `gm! 🌅 Can you tell me my current rewards for address ${address}? Also, when is the next reward distribution?`
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch rewards');
      }

      const data = await response.json();
      return {
        message: data.message,
        success: data.success,
        error: data.error,
        data: data.data
      };
    } catch (error) {
      console.error('Error getting rewards:', error);
      throw error;
    }
  }

  async stake(amount: bigint, address: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `I want to stake ${amount} ETH from address ${address}`
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to stake');
      }

      const data = await response.json();
      return {
        message: data.message,
        success: data.success,
        error: data.error,
        data: data.data
      };
    } catch (error) {
      console.error('Error staking:', error);
      throw error;
    }
  }

  async getStakedAmount(address: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `How much ETH do I have staked at address ${address}?`
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get staked amount');
      }

      const data = await response.json();
      return {
        message: data.message,
        success: data.success,
        error: data.error,
        data: data.data
      };
    } catch (error) {
      console.error('Error getting staked amount:', error);
      throw error;
    }
  }

  async scheduleStake(amount: bigint, address: string, startDate: string, endDate: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `Please schedule a stake of ${amount} ETH from address ${address} starting on ${startDate} and ending on ${endDate}`
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to schedule stake');
      }

      const data = await response.json();
      return {
        message: data.message,
        success: data.success,
        error: data.error,
        data: data.data
      };
    } catch (error) {
      console.error('Error scheduling stake:', error);
      throw error;
    }
  }

  async setupAutoCompound(address: string, frequency: 'daily' | 'weekly' | 'monthly'): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `Please set up auto-compounding for my staking rewards at address ${address} with ${frequency} frequency`
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to setup auto-compound');
      }

      const data = await response.json();
      return {
        message: data.message,
        success: data.success,
        error: data.error,
        data: data.data
      };
    } catch (error) {
      console.error('Error setting up auto-compound:', error);
      throw error;
    }
  }

  async getScheduledTransactions(address: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `What are my scheduled transactions for address ${address}?`
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get scheduled transactions');
      }

      const data = await response.json();
      return {
        message: data.message,
        success: data.success,
        error: data.error,
        data: data.data
      };
    } catch (error) {
      console.error('Error getting scheduled transactions:', error);
      throw error;
    }
  }
}
