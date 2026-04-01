/**
 * DashboardPage.tsx — Protected placeholder page for authenticated users.
 *
 * Spec requirements (§2.5):
 *  ✓ Display the authenticated user's first name.
 *  ✓ Display the authenticated user's role.
 *  ✓ Working sign out button that clears auth state and redirects to /login.
 *
 * This is a placeholder for Week 1.  Future sprints will add document
 * listing, upload, and management features here.
 *
 * The component reads user data from Redux state — no API call needed because
 * the login response already stored the user profile via setCredentials.
 */

import React from 'react';
import { Button, Card, Layout, Tag, Typography } from 'antd';
import { LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { clearCredentials, selectCurrentUser } from '../store/authSlice';

const { Header, Content } = Layout;
const { Title, Text } = Typography;

const DashboardPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  // Read the current user from Redux state.
  // selectCurrentUser returns null only if the user is logged out, but
  // ProtectedRoute prevents this page from rendering in that case.
  const user = useAppSelector(selectCurrentUser);

  // -------------------------------------------------------------------------
  // Sign out handler
  // Spec: "sign out button that clears auth state and redirects to /login"
  // -------------------------------------------------------------------------
  const handleSignOut = () => {
    // 1. Clear all auth state in Redux (isAuthenticated → false, user → null).
    dispatch(clearCredentials());
    // 2. Redirect to the login page.
    //    replace=true removes /dashboard from history so Back doesn't return here.
    navigate('/login', { replace: true });
  };

  // -------------------------------------------------------------------------
  // Role badge colour — ADMIN gets a gold badge, STAFF gets a blue one.
  // Makes the role visually distinct at a glance.
  // -------------------------------------------------------------------------
  const roleColor = user?.role === 'ADMIN' ? 'gold' : 'blue';

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <Layout style={{ minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      {/* ── Top navigation bar ─────────────────────────────────────────── */}
      <Header
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#fff',
          borderBottom: '1px solid #f0f0f0',
          padding: '0 24px',
          boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
        }}
      >
        {/* Brand name */}
        <Title level={4} style={{ margin: 0, color: '#1677ff' }}>
          Koneza Systems — DMS
        </Title>

        {/* User info + Sign out */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {/* Display the user's role as a coloured tag */}
          <Tag color={roleColor} icon={<UserOutlined />}>
            {user?.role ?? '—'}
          </Tag>

          {/* Display the user's full name */}
          <Text>
            {user?.first_name} {user?.last_name}
          </Text>

          {/* Sign out button */}
          <Button
            icon={<LogoutOutlined />}
            onClick={handleSignOut}
            type="default"
          >
            Sign out
          </Button>
        </div>
      </Header>

      {/* ── Main content area ──────────────────────────────────────────── */}
      <Content style={{ padding: 32 }}>
        <Card
          style={{
            maxWidth: 600,
            margin: '0 auto',
            borderRadius: 8,
            boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
          }}
        >
          {/* Welcome message showing first name (spec requirement) */}
          <Title level={3}>
            Welcome back, {user?.first_name ?? 'User'} 👋
          </Title>

          <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
            You are logged in as a{' '}
            <Tag color={roleColor}>{user?.role ?? '—'}</Tag>.
          </Text>

          <Text type="secondary">
            This is a placeholder dashboard. Debt management features will
            be added in the next sprint.
          </Text>
        </Card>
      </Content>
    </Layout>
  );
};

export default DashboardPage;
