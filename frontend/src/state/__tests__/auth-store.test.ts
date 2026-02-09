import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '../auth-store';
import type { UserPrivate } from '@/lib/types';

// A reusable mock user matching the actual UserPrivate shape
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

describe('auth-store', () => {
  beforeEach(() => {
    // Reset store state between tests
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: true,
    });
    localStorage.clear();
  });

  it('starts unauthenticated', () => {
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
  });

  it('login sets user and tokens', () => {
    useAuthStore.getState().login(mockUser, 'access-token', 'refresh-token');

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user?.email).toBe('test@example.com');
    expect(state.isLoading).toBe(false);
  });

  it('logout clears state', () => {
    useAuthStore.getState().login(mockUser, 'access-token', 'refresh-token');
    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
  });

  it('setLoading updates loading state', () => {
    useAuthStore.getState().setLoading(false);
    expect(useAuthStore.getState().isLoading).toBe(false);
  });

  it('setUser sets user and authentication flag', () => {
    useAuthStore.getState().setUser(mockUser);
    expect(useAuthStore.getState().isAuthenticated).toBe(true);

    useAuthStore.getState().setUser(null);
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });
});
