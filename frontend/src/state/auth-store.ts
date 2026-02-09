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

        // Initialize organization data if user is a newsroom member
        if (user.organization_id) {
          import('./organization-store').then(({ useOrganizationInit }) => {
            const initOrganization = useOrganizationInit();
            initOrganization(user).catch(console.error);
          });
        }
      },

      logout: () => {
        tokenManager.clearTokens();
        set({ user: null, isAuthenticated: false });

        // Clear organization data on logout
        import('./organization-store').then(({ useOrganizationStore }) => {
          useOrganizationStore.getState().reset();
        });
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

      // Initialize organization data if user is a newsroom member
      if (user.organization_id) {
        const { useOrganizationInit } = await import('./organization-store');
        const initOrganization = useOrganizationInit();
        initOrganization(user).catch(console.error);
      }

      return;
    }

    // Otherwise, try to fetch current user
    try {
      const { apiClient } = await import('@/lib/api-client');
      const response = await apiClient.get('/auth/me');
      const userData = response.data;
      setUser(userData);

      // Initialize organization data if user is a newsroom member
      if (userData.organization_id) {
        const { useOrganizationInit } = await import('./organization-store');
        const initOrganization = useOrganizationInit();
        initOrganization(userData).catch(console.error);
      }
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
