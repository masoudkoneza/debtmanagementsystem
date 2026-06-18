/**
 * apiService.ts — Axios instance shared across all API calls.
 *
 * Responsibilities:
 *  1. Set the base URL from the VITE_API_BASE_URL environment variable so
 *     the same build can point at different backends without code changes.
 *  2. Attach the JWT access token to every outgoing request via a request
 *     interceptor — components never have to add Authorization headers manually.
 *  3. Provide a response interceptor hook for future 401→refresh logic.
 *
 * Why an interceptor instead of a default header?
 *  Default headers are set once at startup.  The user is not logged in at
 *  startup, so the token is not available yet.  An interceptor runs just
 *  before each request, reading the current token from the Redux store at
 *  that moment.
 *
 * Security note:
 *  The token is read from the Redux store (in-memory), never from
 *  localStorage or document.cookie.  This is intentional — see authSlice.ts.
 */

import axios from 'axios';
import { store } from '../store/store';
import { selectAccessToken } from '../store/authSlice';

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------

const apiClient = axios.create({
  // VITE_API_BASE_URL is set in .env (e.g. http://localhost:8000).
  // Vite injects env vars prefixed with VITE_ at build time.
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',

  headers: {
    'Content-Type': 'application/json',
  },
});

// ---------------------------------------------------------------------------
// Request interceptor — attach Bearer token
// ---------------------------------------------------------------------------

apiClient.interceptors.request.use(
  (config) => {
    // Read the current token from Redux state at request time.
    // Returns null when the user is not logged in.
    const token = selectAccessToken(store.getState());

    if (token) {
      // Set the Authorization header expected by Django/simplejwt.
      // Format:  Authorization: Bearer <JWT>
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    // Pass request setup errors through unchanged.
    return Promise.reject(error);
  }
);

// ---------------------------------------------------------------------------
// Response interceptor — centralised error handling hook
// ---------------------------------------------------------------------------

apiClient.interceptors.response.use(
  // Pass successful responses straight through.
  (response) => response,

  (error) => {
    // Future enhancement: if error.response?.status === 401, attempt a
    // silent token refresh using the refresh token stored in an HttpOnly
    // cookie, then retry the original request.  Out of scope for Week 1.
    return Promise.reject(error);
  }
);

export default apiClient;
