/**
 * LoginPage.tsx — The public login screen for the DMS.
 *
 * Spec requirements (§2.3):
 *  ✓ Centered card layout with "Koneza Systems" heading above the form.
 *  ✓ Email field: Ant Design Input, type email, required, label "Email address".
 *  ✓ Password field: Ant Design Input.Password, label "Password", required.
 *  ✓ Submit button: full width, text "Sign in", loading spinner during request.
 *  ✓ Submit button disabled while request is in flight.
 *  ✓ Error: Ant Design Alert (type error) shown below button on failed login.
 *  ✓ Error dismissed when user starts typing in either field.
 *  ✓ On success: navigate to /dashboard immediately.
 *  ✓ Redirect to /dashboard if already authenticated (prevents re-login).
 *
 * State managed locally (not in Redux) because it is transient UI state
 * that no other component needs:
 *  - loading    — true while the API request is in flight.
 *  - errorMsg   — the error text shown in the Alert, or null when hidden.
 */

import React, { useState } from 'react';
import { Alert, Button, Card, Form, Input, Typography } from 'antd';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { selectIsAuthenticated, setCredentials } from '../store/authSlice';
import { login } from '../services/authService';
import type { AuthUser } from '../store/authSlice';
import BrandLogo from '../components/BrandLogo';

const { Title } = Typography;

// ---------------------------------------------------------------------------
// Form field type — keeps Form.useForm and form values in sync with TS.
// ---------------------------------------------------------------------------
interface LoginFormValues {
  email: string;
  password: string;
}

const LoginPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);

  // -------------------------------------------------------------------------
  // Local UI state
  // -------------------------------------------------------------------------
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Ant Design Form instance — gives us programmatic access to field values
  // and lets us trigger validation from the submit handler.
  const [form] = Form.useForm<LoginFormValues>();

  // -------------------------------------------------------------------------
  // Redirect if already authenticated
  // Spec: "/login → Redirect to /dashboard if already authenticated."
  // -------------------------------------------------------------------------
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  // -------------------------------------------------------------------------
  // Submit handler
  // -------------------------------------------------------------------------
  const handleSubmit = async (values: LoginFormValues) => {
    setLoading(true);
    setErrorMsg(null); // Clear any previous error before the new attempt.

    try {
      const data = await login(values.email, values.password);

      // Build the full AuthUser shape from the login response.
      // The login endpoint returns a subset of fields; /me returns all fields.
      // For the dashboard we only need what login returns (first_name, role).
      const user: AuthUser = {
        ...data.user,
        tenant_id: null,         // Not returned by login; null is safe default.
        date_joined: '',         // Not returned by login; populated by /me later.
      };

      // Store the credentials in Redux — this sets isAuthenticated=true and
      // causes ProtectedRoute to grant access to /dashboard.
      dispatch(setCredentials({ user, accessToken: data.access_token }));

      // Navigate immediately on success (spec: "Navigate to /dashboard immediately").
      navigate('/dashboard', { replace: true });

    } catch (error: unknown) {
      // Map HTTP status codes to user-friendly messages.
      const axiosError = error as { response?: { status?: number } };
      const status = axiosError.response?.status;

      if (status === 401) {
        setErrorMsg('Invalid email address or password. Please try again.');
      } else if (status === 403) {
        setErrorMsg('Your account has been deactivated. Please contact your administrator.');
      } else if (status === 400) {
        setErrorMsg('Please fill in all required fields.');
      } else {
        // Catch-all for network errors, 500s, etc.
        setErrorMsg('Something went wrong. Please try again later.');
      }
    } finally {
      // Always clear the loading state, whether the request succeeded or failed.
      setLoading(false);
    }
  };

  // -------------------------------------------------------------------------
  // Dismiss error when the user starts typing
  // Spec: "Dismissed when user starts typing."
  // -------------------------------------------------------------------------
  const handleFieldChange = () => {
    if (errorMsg) {
      setErrorMsg(null);
    }
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <div
      style={{
        // Full-viewport centered layout — card sits in the middle of the screen.
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#f0f2f5', // Ant Design's standard page background.
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
          borderRadius: 8,
        }}
      >
        {/* ── Heading (spec: "Koneza Systems heading above the form") ───── */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <BrandLogo />
        </div>

        {/* ── Login form ─────────────────────────────────────────────────── */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          // Disable browser's built-in validation so Ant Design handles it.
          noValidate
        >
          {/* Email field */}
          <Form.Item
            name="email"
            label="Email address"
            rules={[
              { required: true, message: 'Email address is required.' },
              { type: 'email', message: 'Please enter a valid email address.' },
            ]}
          >
            <Input
              type="email"
              placeholder="you@example.com"
              autoComplete="email"
              // Dismiss the error Alert as soon as the user starts correcting input.
              onChange={handleFieldChange}
              disabled={loading}
            />
          </Form.Item>

          {/* Password field */}
          <Form.Item
            name="password"
            label="Password"
            rules={[{ required: true, message: 'Password is required.' }]}
          >
            {/* Input.Password adds the show/hide toggle eye icon. */}
            <Input.Password
              placeholder="Your password"
              autoComplete="current-password"
              onChange={handleFieldChange}
              disabled={loading}
            />
          </Form.Item>

          {/* Submit button */}
          <Form.Item style={{ marginBottom: errorMsg ? 12 : 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              block                   // Full width (spec requirement).
              loading={loading}       // Shows spinner while request is in flight.
              disabled={loading}      // Prevents double-submission.
            >
              Sign in
            </Button>
          </Form.Item>

          {/* Error Alert — only rendered when errorMsg is non-null.
              Placed below the button per spec. */}
          {errorMsg && (
            <Alert
              type="error"
              message={errorMsg}
              showIcon
              closable
              onClose={() => setErrorMsg(null)}
              style={{ marginTop: 0 }}
            />
          )}
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;
