// app/api/login/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getIronSession } from 'iron-session';
import { sessionOptions } from '@/lib/session';
import { SessionData } from '@/types';


// Store tokens in memory (in production, use Redis)
import { userTokens } from '@/lib/token-store';

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    // Call Python API instead of local validation
    const authResponse = await fetch(`${PYTHON_API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    
    if (!authResponse.ok) {
      const error = await authResponse.json();
      return NextResponse.json(
        { success: false, error: error.detail || 'Invalid credentials' },
        { status: authResponse.status }
      );
    }

    const authData = await authResponse.json();
    
    // Store the JWT token for later use
    userTokens.set(email, authData.access_token);

    console.log('User authenticated:', userTokens);

    const response = NextResponse.json({
      success: true,
      user: email,
      access: authData.access_level as 'setosa' | 'virginica'
    });

    const session = await getIronSession<SessionData>(request, response, sessionOptions);
    session.user = email;
    session.access = authData.access_level as 'setosa' | 'virginica';
    await session.save();

    return response;
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Server error' },
      { status: 500 }
    );
  }
}