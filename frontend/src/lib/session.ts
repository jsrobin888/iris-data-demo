import { SessionOptions } from 'iron-session';
import { SessionData } from '@/types';

export const sessionOptions: SessionOptions = {
  password: process.env.SESSION_SECRET || 'complex_password_at_least_32_characters_long',
  cookieName: 'iris-viewer-session',
  cookieOptions: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    sameSite: 'lax',
  },
};

// This is where we specify the typings of req.session.*
declare module 'iron-session' {
  interface IronSessionData extends SessionData {}
}