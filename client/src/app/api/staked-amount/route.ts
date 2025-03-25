import { NextResponse } from 'next/server';
import { StakingService } from '@/services/staking';
import { isAddress } from 'viem';

const stakingService = new StakingService();

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const address = searchParams.get('address');

    if (!address) {
      return NextResponse.json(
        { error: 'Address parameter is required' },
        { status: 400 }
      );
    }

    if (!isAddress(address)) {
      return NextResponse.json(
        { error: 'Invalid Ethereum address' },
        { status: 400 }
      );
    }

    const stakedAmount = await stakingService.getStakedAmount(address as `0x${string}`);

    return NextResponse.json({ stakedAmount });
  } catch (error) {
    console.error('Error getting staked amount:', error);
    return NextResponse.json(
      { error: 'Failed to get staked amount' },
      { status: 500 }
    );
  }
}
