import { describe, it, expect, beforeEach } from 'vitest';
import { tokenManager, getErrorMessage } from '../api-client';

describe('tokenManager', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('stores and retrieves tokens', () => {
    tokenManager.setTokens('access-123', 'refresh-456');
    expect(tokenManager.getAccessToken()).toBe('access-123');
    expect(tokenManager.getRefreshToken()).toBe('refresh-456');
  });

  it('returns null when no tokens', () => {
    expect(tokenManager.getAccessToken()).toBeNull();
    expect(tokenManager.getRefreshToken()).toBeNull();
  });

  it('clears tokens', () => {
    tokenManager.setTokens('access', 'refresh');
    tokenManager.clearTokens();
    expect(tokenManager.getAccessToken()).toBeNull();
    expect(tokenManager.getRefreshToken()).toBeNull();
  });
});

describe('getErrorMessage', () => {
  it('returns message from Error instance', () => {
    expect(getErrorMessage(new Error('something broke'))).toBe('something broke');
  });

  it('returns fallback for unknown types', () => {
    expect(getErrorMessage(42)).toBe('An unexpected error occurred');
  });
});
