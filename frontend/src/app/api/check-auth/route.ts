import { NextRequest, NextResponse } from 'next/server';
import { getIronSession } from 'iron-session';
import { sessionOptions } from '@/lib/session';
import { SessionData } from '@/types';

export async function GET(request: NextRequest) {
  const response = NextResponse.json({ authenticated: false });
  const session = await getIronSession<SessionData>(request, response, sessionOptions);

  if (session.user) {
    return NextResponse.json({
      authenticated: true,
      user: session.user,
      access: session.access
    });
  }

  return response;
}