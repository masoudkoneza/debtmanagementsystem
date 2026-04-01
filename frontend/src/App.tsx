/**
 * App.tsx — Root component: sets up React Router with public and protected routes.
 *
 * Route table (spec §2.2):
 *
 *  /login      → LoginPage      Public.  Redirects to /dashboard if already authenticated.
 *  /dashboard  → DashboardPage  Protected. Redirects to /login if not authenticated.
 *  /           → Redirect to /login (convenience default).
 *
 * Route protection is handled by ProtectedRoute, which wraps all private routes
 * in a single outlet.  Adding new protected routes in the future only requires
 * nesting them inside the ProtectedRoute element — no other changes needed.
 */

import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ProtectedRoute from './components/ProtectedRoute';

const App: React.FC = () => {
  return (
    <Routes>
      {/* ── Public routes ─────────────────────────────────────────────── */}
      {/*
        LoginPage handles its own "already authenticated" redirect internally
        (see LoginPage.tsx) so we don't need a wrapper here.
      */}
      <Route path="/login" element={<LoginPage />} />

      {/* ── Protected routes (require authentication) ─────────────────── */}
      {/*
        ProtectedRoute checks isAuthenticated.  If false, it redirects to
        /login before the child route ever renders.
      */}
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<DashboardPage />} />
      </Route>

      {/* ── Fallback — redirect root and any unknown paths to /login ───── */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

export default App;
