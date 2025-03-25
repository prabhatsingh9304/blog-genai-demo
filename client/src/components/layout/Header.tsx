'use client';

import { useState } from 'react';
import { ConnectButton } from '../ConnectButton';

export const Header = () => {
  return (
    <header className="w-full border-b border-gray-200 bg-white/75 backdrop-blur-xl">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center space-x-4">
          <span className="text-xl font-bold">🥩 Stake Mate</span>
        </div>
        <div className="flex items-center space-x-4">
          <ConnectButton />
        </div>
      </div>
    </header>
  );
};
