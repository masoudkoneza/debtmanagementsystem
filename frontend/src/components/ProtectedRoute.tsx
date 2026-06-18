/**
 * ProtectedRoute.tsx — Route guard for authenticated-only pages.
 *
 * How it works:
 *  1. Reads isAuthenticated from Redux state.
 *  2. If false, redirects the user to /login, replacing the current history
 *     entry so the browser Back button does not loop back to the protected page.
 *  3. If true, renders the child route element unchanged.
 *
 * Usage in App.tsx:
 *   <Route element={<ProtectedRoute />}>
 *     <Route path="/dashboard" element={<DashboardPage />} />
 *   </Route>
 *
 * The <Outlet /> renders whatever child route was matched — so this component
 * does not need to know which page it is protecting.
 */

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';
import { selectIsAuthenticated } from '../store/authSlice';

const ProtectedRoute: React.FC = () => {
  const isAuthenticated = useAppSelector(selectIsAuthenticated);

  if (!isAuthenticated) {
    // replace=true prevents the protected URL from being added to history,
    // so clicking Back after a redirect goes further back rather than looping.
    return <Navigate to="/login" replace />;
  }

  // Render the matched child route (e.g. DashboardPage).
  return <Outlet />;
};

export default ProtectedRoute;
