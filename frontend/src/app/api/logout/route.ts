// app/api/logout/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getIronSession } from 'iron-session';
import { sessionOptions } from '@/lib/session';
import { SessionData } from '@/types';
import { userTokens } from '../login/route';

export async function POST(request: NextRequest) {
  const response = NextResponse.json({ success: true });
  const session = await getIronSession<SessionData>(request, response, sessionOptions);
  
  // Clean up the stored token
  if (session.user) {
    userTokens.delete(session.user);
  }
  
  session.destroy();
  
  return response;
}