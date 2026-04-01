/**
 * authSlice.ts — Redux slice for authentication state.
 *
 * Responsibilities:
 *  - Hold the current user object, access token, and auth status.
 *  - Expose two actions: setCredentials (login) and clearCredentials (logout).
 *  - Provide typed selector hooks so components never access state.auth directly.
 *
 * Security decision:
 *  The access token lives in Redux state ONLY — never in localStorage or
 *  sessionStorage.  This prevents XSS attacks from reading the token via
 *  document.cookie or localStorage.getItem().  The trade-off is that a page
 *  refresh clears the token, so the user must log in again.
 *  (A refresh-token flow stored in an HttpOnly cookie is the production solution,
 *  but is out of scope for Week 1.)
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from './store';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Shape of the user object stored in Redux (mirrors the /me API response). */
export interface AuthUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: 'ADMIN' | 'STAFF';
  tenant_id: string | null;
  date_joined: string;
}

/** The full auth slice state. */
interface AuthState {
  /** Authenticated user profile, or null when logged out. */
  user: AuthUser | null;
  /** JWT access token, or null when logged out. */
  accessToken: string | null;
  /** Convenience flag — true when both user and accessToken are present. */
  isAuthenticated: boolean;
}

// ---------------------------------------------------------------------------
// Initial state — unauthenticated on every page load.
// ---------------------------------------------------------------------------

const initialState: AuthState = {
  user: null,
  accessToken: null,
  isAuthenticated: false,
};

// ---------------------------------------------------------------------------
// Slice
// ---------------------------------------------------------------------------

const authSlice = createSlice({
  name: 'auth',
  initialState,

  reducers: {
    /**
     * setCredentials — called immediately after a successful login response.
     *
     * Receives the access token and user object from the API and stores them
     * in Redux state.  Setting isAuthenticated to true here is what causes
     * ProtectedRoute to allow access to /dashboard.
     */
    setCredentials(
      state,
      action: PayloadAction<{ user: AuthUser; accessToken: string }>
    ) {
      state.user = action.payload.user;
      state.accessToken = action.payload.accessToken;
      state.isAuthenticated = true;
    },

    /**
     * clearCredentials — called when the user clicks Sign out.
     *
     * Resets all auth state to the initial (logged-out) values.
     * ProtectedRoute detects isAuthenticated=false and redirects to /login.
     */
    clearCredentials(state) {
      state.user = null;
      state.accessToken = null;
      state.isAuthenticated = false;
    },
  },
});

// ---------------------------------------------------------------------------
// Actions (exported for use in components and thunks)
// ---------------------------------------------------------------------------
export const { setCredentials, clearCredentials } = authSlice.actions;

// ---------------------------------------------------------------------------
// Selectors — typed helpers so components don't couple to state shape.
// ---------------------------------------------------------------------------

/** Returns true when the user is logged in. */
export const selectIsAuthenticated = (state: RootState) =>
  state.auth.isAuthenticated;

/** Returns the current user object, or null when logged out. */
export const selectCurrentUser = (state: RootState) => state.auth.user;

/** Returns the JWT access token, or null when logged out. */
export const selectAccessToken = (state: RootState) => state.auth.accessToken;

export default authSlice.reducer;
