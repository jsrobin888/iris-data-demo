export interface User {
  email: string;
  access: 'setosa' | 'virginica';
}

export interface IrisData {
  sepal_length: number[];
  sepal_width: number[];
  petal_length: number[];
  petal_width: number[];
  species: string;
}

export interface LoginResponse {
  success: boolean;
  user?: string;
  access?: string;
  error?: string;
}

export interface AuthResponse {
  authenticated: boolean;
  user?: string;
  access?: string;
}

export interface SessionData {
  user?: string;
  access?: 'setosa' | 'virginica';
}