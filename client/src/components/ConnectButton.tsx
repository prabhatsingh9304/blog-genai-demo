'use client';

import { useState } from 'react';

export const ConnectButton = () => {
  const [connected, setConnected] = useState(false);

  const handleConnect = () => {
    setConnected(!connected);
  };

  return (
    <button
      onClick={handleConnect}
      className="px-4 py-2 bg-gray-200 text-black rounded hover:bg-gray-300"
    >
      {connected ? 'Connected' : 'Connect Wallet'}
    </button>
  );
};
