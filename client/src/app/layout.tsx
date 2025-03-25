import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Staking Optimizer',
  description: 'Optimize your staking rewards with AI-powered strategies',
  keywords: ['staking', 'ethereum', 'defi', 'optimization', 'rewards'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
