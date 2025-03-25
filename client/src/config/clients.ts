import { createPublicClient, createWalletClient, custom, http } from 'viem';
import { mainnet } from 'viem/chains';

export const publicClient = createPublicClient({
  chain: mainnet,
  transport: http(),
});

// Check if window exists (for SSR) and if ethereum is available
export const walletClient = 
  typeof window !== 'undefined' && 
  'ethereum' in window && 
  window.ethereum
    ? createWalletClient({
        chain: mainnet,
        transport: custom(window.ethereum as any),
      })
    : null;
