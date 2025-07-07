interface UserDB {
  [email: string]: {
    password: string;
    access: 'setosa' | 'virginica';
  };
}

// Simple user database (in production, use proper hashing and database)
const USERS: UserDB = {
  'setosa@example.com': {
    password: 'password123',
    access: 'setosa'
  },
  'virginica@example.com': {
    password: 'password123',
    access: 'virginica'
  }
};

export function validateUser(email: string, password: string) {
  const user = USERS[email];
  if (user && user.password === password) {
    return {
      email,
      access: user.access
    };
  }
  return null;
}

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}