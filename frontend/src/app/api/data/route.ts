import { NextRequest, NextResponse } from 'next/server';
import { getIronSession } from 'iron-session';
import { sessionOptions } from '@/lib/session';
import { SessionData } from '@/types';

// Python API configuration
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';
const PYTHON_API_KEY = process.env.PYTHON_API_KEY || ''; // Optional API key

export async function GET(request: NextRequest) {
  const response = NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  const session = await getIronSession<SessionData>(request, response, sessionOptions);

  if (!session.user || !session.access) {
    return response;
  }

  try {
    // Call Python API to get data
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Add API key if configured
    if (PYTHON_API_KEY) {
      headers['X-API-Key'] = PYTHON_API_KEY;
    }

    const pythonResponse = await fetch(
      `${PYTHON_API_URL}/api/data/${session.access}`,
      {
        method: 'GET',
        headers,
      }
    );

    if (!pythonResponse.ok) {
      const errorData = await pythonResponse.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch data from data service' },
        { status: pythonResponse.status }
      );
    }

    const data = await pythonResponse.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Error calling Python API:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data from data service' },
      { status: 500 }
    );
  }
}