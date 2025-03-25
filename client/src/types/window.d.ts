import { type WalletClient } from 'viem';

declare global {
  interface Window {
    ethereum?: WalletClient;
  }
}
