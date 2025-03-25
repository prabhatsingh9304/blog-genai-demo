import { NextResponse } from 'next/server';
import { isAddress } from 'viem';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { amount, address, timestamp } = body;

    if (!amount || !address || !timestamp) {
      return NextResponse.json(
        { error: 'Amount, address, and timestamp are required' },
        { status: 400 }
      );
    }

    if (!isAddress(address)) {
      return NextResponse.json(
        { error: 'Invalid address parameter' },
        { status: 400 }
      );
    }

    const response = await fetch(`${BACKEND_URL}/api/schedule-stake`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        address,
        amount: amount.toString(),
        timestamp,
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.statusText}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in schedule-stake endpoint:', error);
    return NextResponse.json(
      { error: 'Failed to schedule stake' },
      { status: 500 }
    );
  }
}
