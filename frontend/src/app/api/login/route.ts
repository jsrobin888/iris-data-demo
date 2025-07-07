import { NextRequest, NextResponse } from 'next/server';
import { getIronSession } from 'iron-session';
import { sessionOptions } from '@/lib/session';
import { validateUser } from '@/lib/auth';
import { SessionData } from '@/types';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    const user = validateUser(email, password);
    
    if (!user) {
      return NextResponse.json(
        { success: false, error: 'Invalid credentials' },
        { status: 401 }
      );
    }

    const response = NextResponse.json({
      success: true,
      user: user.email,
      access: user.access
    });

    const session = await getIronSession<SessionData>(request, response, sessionOptions);
    session.user = user.email;
    session.access = user.access;
    await session.save();

    return response;
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Server error' },
      { status: 500 }
    );
  }
}