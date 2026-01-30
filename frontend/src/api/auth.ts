import { apiPost } from "./client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
}

export async function register(data: RegisterRequest): Promise<UserResponse> {
  return apiPost("/auth/register", data);
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  return apiPost("/auth/login", data);
}

export async function refreshToken(refreshToken: string): Promise<TokenResponse> {
  return apiPost("/auth/refresh", { refresh_token: refreshToken });
}

export function setTokens(response: TokenResponse) {
  localStorage.setItem("access_token", response.access_token);
  localStorage.setItem("refresh_token", response.refresh_token);
}

export function getAccessToken(): string | null {
  return localStorage.getItem("access_token");
}

export function getRefreshToken(): string | null {
  return localStorage.getItem("refresh_token");
}

export function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}
