/**
 * authService.ts — Functions that call the DMS authentication API.
 *
 * All three functions correspond directly to spec §2.4:
 *  - login(email, password)  → POST /api/auth/login
 *  - refreshToken(refresh)   → POST /api/auth/refresh
 *  - getMe()                 → GET  /api/auth/me
 *
 * Why a dedicated service layer?
 *  Keeping API calls out of components makes them easier to test, swap, and
 *  mock.  Components import from authService; they don't know or care which
 *  HTTP library is used underneath.
 *
 * Error handling:
 *  Functions do NOT catch errors — they let Axios errors propagate to the
 *  caller (LoginPage, etc.) where the appropriate UI feedback can be shown.
 *  This keeps the service layer thin and side-effect-free.
 */

import apiClient from './apiService';
import type { AuthUser } from '../store/authSlice';

// ---------------------------------------------------------------------------
// Response type definitions
// ---------------------------------------------------------------------------

/** Shape returned by POST /api/auth/login (200). */
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: Pick<AuthUser, 'id' | 'email' | 'first_name' | 'last_name' | 'role'>;
}

/** Shape returned by POST /api/auth/refresh (200). */
export interface RefreshResponse {
  access_token: string;
}

// ---------------------------------------------------------------------------
// Service functions
// ---------------------------------------------------------------------------

/**
 * login — Exchange email + password for JWT tokens.
 *
 * @throws AxiosError with status 400 (missing fields),
 *                                  401 (bad credentials),
 *                                  403 (inactive account).
 */
export async function login(
  email: string,
  password: string
): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/api/auth/login', {
    email,
    password,
  });
  return response.data;
}

/**
 * refreshToken — Exchange a refresh token for a new access token.
 *
 * Called when the access token has expired (15 min) but the refresh token
 * is still valid (7 days).  Allows silent re-authentication.
 *
 * @param refresh The refresh token string from the original login response.
 * @throws AxiosError with status 401 if the refresh token is invalid/expired.
 */
export async function refreshToken(refresh: string): Promise<RefreshResponse> {
  const response = await apiClient.post<RefreshResponse>('/api/auth/refresh', {
    refresh,
  });
  return response.data;
}

/**
 * getMe — Fetch the current user's full profile.
 *
 * Requires a valid Bearer token to be in Redux state (attached automatically
 * by the Axios request interceptor in apiService.ts).
 *
 * @throws AxiosError with status 401 if no token is present or it is expired.
 */
export async function getMe(): Promise<AuthUser> {
  const response = await apiClient.get<AuthUser>('/api/auth/me');
  return response.data;
}
