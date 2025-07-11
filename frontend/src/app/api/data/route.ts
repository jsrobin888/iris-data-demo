// app/api/data/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getIronSession } from 'iron-session';
import { sessionOptions } from '@/lib/session';
import { SessionData, IrisData } from '@/types';
import { userTokens } from '../login/route';

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';
const PYTHON_API_KEY = process.env.PYTHON_API_KEY || '';

export async function GET(request: NextRequest) {
  const session = await getIronSession<SessionData>(request, NextResponse.next(), sessionOptions);
  console.log('Session data:', session, session.user, session.access );
  if (!session.user) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  }

  // Get the JWT token
  const token = userTokens.get(session.user);

  console.log('Token for user:', session.user, token);
  if (!token) {
    return NextResponse.json({ error: 'Session expired. Please login again.' }, { status: 401 });
  }

  try {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`, // Add JWT token here
    };
    
    if (PYTHON_API_KEY) {
      headers['X-API-Key'] = PYTHON_API_KEY;
    }

    // Call my-data endpoint to get user's species data
    const pythonResponse = await fetch(
      `${PYTHON_API_URL}/api/v1/data/my-data`,
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

    const apiData = await pythonResponse.json();
    
    // Transform the response to match IrisData interface
    const irisData: IrisData = {
      species: apiData.species,
      sepal_length: apiData.data.map((d: any) => d.sepal_length),
      sepal_width: apiData.data.map((d: any) => d.sepal_width),
      petal_length: apiData.data.map((d: any) => d.petal_length),
      petal_width: apiData.data.map((d: any) => d.petal_width),
    };

    return NextResponse.json(irisData);
    
  } catch (error) {
    console.error('Error calling Python API:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data from data service' },
      { status: 500 }
    );
  }
}