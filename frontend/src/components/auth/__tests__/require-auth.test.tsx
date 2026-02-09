import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RequireAuth } from '../require-auth';
import { useAuthStore } from '@/state/auth-store';
import type { UserPrivate } from '@/lib/types';

const mockUser: UserPrivate = {
  id: '1',
  handle: 'testuser',
  display_name: 'Test User',
  avatar_url: null,
  bio: null,
  receipt_count: 0,
  created_at: '2024-01-01T00:00:00Z',
  email: 'test@example.com',
  is_verified: false,
  is_moderator: false,
  updated_at: null,
  last_login_at: null,
};

describe('RequireAuth', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it('shows spinner when loading', () => {
    useAuthStore.setState({ isLoading: true });
    render(
      <RequireAuth>
        <div>Protected content</div>
      </RequireAuth>
    );
    // While loading, children are not rendered
    expect(screen.queryByText('Protected content')).not.toBeInTheDocument();
  });

  it('renders children when authenticated', () => {
    useAuthStore.setState({
      isAuthenticated: true,
      isLoading: false,
      user: mockUser,
    });
    render(
      <RequireAuth>
        <div>Protected content</div>
      </RequireAuth>
    );
    expect(screen.getByText('Protected content')).toBeInTheDocument();
  });

  it('does not render children when not authenticated', () => {
    useAuthStore.setState({ isAuthenticated: false, isLoading: false });
    render(
      <RequireAuth>
        <div>Protected content</div>
      </RequireAuth>
    );
    expect(screen.queryByText('Protected content')).not.toBeInTheDocument();
  });

  it('blocks non-moderator from moderator route', () => {
    useAuthStore.setState({
      isAuthenticated: true,
      isLoading: false,
      user: { ...mockUser, is_moderator: false },
    });
    render(
      <RequireAuth requireModerator>
        <div>Admin content</div>
      </RequireAuth>
    );
    expect(screen.queryByText('Admin content')).not.toBeInTheDocument();
  });
});
