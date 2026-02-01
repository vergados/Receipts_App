import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UserPrivate } from '@/lib/types';
import { tokenManager } from '@/lib/api-client';

interface AuthState {
  user: UserPrivate | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: UserPrivate | null) => void;
  login: (user: UserPrivate, accessToken: string, refreshToken: string) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      
      setUser: (user) => {
        set({ user, isAuthenticated: !!user });
      },
      
      login: (user, accessToken, refreshToken) => {
        tokenManager.setTokens(accessToken, refreshToken);
        set({ user, isAuthenticated: true, isLoading: false });
      },
      
      logout: () => {
        tokenManager.clearTokens();
        set({ user: null, isAuthenticated: false });
      },
      
      setLoading: (isLoading) => {
        set({ isLoading });
      },
    }),
    {
      name: 'receipts-auth',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);

// Hook to check if user is authenticated on mount
export function useAuthInit() {
  const { setLoading, setUser, isAuthenticated, user } = useAuthStore();
  
  // Check if we have a token and validate it
  const checkAuth = async () => {
    const token = tokenManager.getAccessToken();
    
    if (!token) {
      setLoading(false);
      return;
    }
    
    // If we have cached user data, we're probably good
    if (isAuthenticated && user) {
      setLoading(false);
      return;
    }
    
    // Otherwise, try to fetch current user
    try {
      const { apiClient } = await import('@/lib/api-client');
      const response = await apiClient.get('/auth/me');
      setUser(response.data);
    } catch {
      // Token invalid, clear it
      tokenManager.clearTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };
  
  return checkAuth;
}
