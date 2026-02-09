import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  Organization,
  Department,
  OrganizationMember,
  OrganizationInvite,
  InvestigationThread,
  OrganizationCreate,
  OrganizationUpdate,
  DepartmentCreate,
  InviteCreate,
  MemberUpdateRole,
  InvestigationCreate,
  InvestigationUpdate,
} from '@/lib/types';

interface OrganizationState {
  // Current user's organization (if member)
  currentOrganization: Organization | null;
  currentOrgMembers: OrganizationMember[];
  currentOrgDepartments: Department[];
  currentOrgInvestigations: InvestigationThread[];

  // Directory of all verified organizations (cached)
  organizations: Organization[];

  // Selected organization (for viewing profiles)
  selectedOrganization: Organization | null;
  selectedOrgMembers: OrganizationMember[];
  selectedOrgDepartments: Department[];

  // Loading states
  isLoading: boolean;
  isLoadingMembers: boolean;
  isLoadingDepartments: boolean;
  isLoadingInvestigations: boolean;

  // Error state
  error: string | null;

  // Actions - Organization Management
  setCurrentOrganization: (org: Organization | null) => void;
  loadOrganizationList: () => Promise<void>;
  createOrganization: (data: OrganizationCreate) => Promise<Organization>;
  updateOrganization: (orgId: string, data: OrganizationUpdate) => Promise<Organization>;
  getOrganization: (slug: string) => Promise<Organization>;
  setSelectedOrganization: (org: Organization | null) => void;

  // Actions - Member Management
  loadCurrentOrgMembers: () => Promise<void>;
  loadSelectedOrgMembers: (orgId: string) => Promise<void>;
  updateMemberRole: (orgId: string, userId: string, role: MemberUpdateRole) => Promise<void>;
  removeMember: (orgId: string, userId: string) => Promise<void>;

  // Actions - Department Management
  loadCurrentOrgDepartments: () => Promise<void>;
  loadSelectedOrgDepartments: (orgId: string) => Promise<void>;
  createDepartment: (orgId: string, data: DepartmentCreate) => Promise<Department>;

  // Actions - Invitation Management
  sendInvitation: (orgId: string, data: InviteCreate) => Promise<OrganizationInvite>;
  acceptInvitation: (token: string) => Promise<void>;

  // Actions - Investigation Management
  loadCurrentOrgInvestigations: () => Promise<void>;
  createInvestigation: (data: InvestigationCreate) => Promise<InvestigationThread>;
  updateInvestigation: (id: string, data: InvestigationUpdate) => Promise<InvestigationThread>;
  publishInvestigation: (id: string) => Promise<InvestigationThread>;
  deleteInvestigation: (id: string) => Promise<void>;

  // Utility actions
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  currentOrganization: null,
  currentOrgMembers: [],
  currentOrgDepartments: [],
  currentOrgInvestigations: [],
  organizations: [],
  selectedOrganization: null,
  selectedOrgMembers: [],
  selectedOrgDepartments: [],
  isLoading: false,
  isLoadingMembers: false,
  isLoadingDepartments: false,
  isLoadingInvestigations: false,
  error: null,
};

export const useOrganizationStore = create<OrganizationState>()(
  persist(
    (set, get) => ({
      ...initialState,

      // Organization Management
      setCurrentOrganization: (org) => {
        set({ currentOrganization: org });
      },

      loadOrganizationList: async () => {
        set({ isLoading: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.get<Organization[]>('/organizations');
          set({ organizations: response.data, isLoading: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to load organizations',
            isLoading: false
          });
          throw error;
        }
      },

      createOrganization: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.post<Organization>('/organizations', data);
          const newOrg = response.data;

          // Add to organizations list
          set({
            organizations: [...get().organizations, newOrg],
            isLoading: false
          });

          return newOrg;
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to create organization',
            isLoading: false
          });
          throw error;
        }
      },

      updateOrganization: async (orgId, data) => {
        set({ isLoading: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.patch<Organization>(`/organizations/${orgId}`, data);
          const updatedOrg = response.data;

          // Update in current organization if it's the same
          if (get().currentOrganization?.id === orgId) {
            set({ currentOrganization: updatedOrg });
          }

          // Update in organizations list
          set({
            organizations: get().organizations.map(org =>
              org.id === orgId ? updatedOrg : org
            ),
            isLoading: false
          });

          return updatedOrg;
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to update organization',
            isLoading: false
          });
          throw error;
        }
      },

      getOrganization: async (slug) => {
        set({ isLoading: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.get<Organization>(`/organizations/${slug}`);
          set({ isLoading: false });
          return response.data;
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to load organization',
            isLoading: false
          });
          throw error;
        }
      },

      setSelectedOrganization: (org) => {
        set({ selectedOrganization: org });
      },

      // Member Management
      loadCurrentOrgMembers: async () => {
        const org = get().currentOrganization;
        if (!org) return;

        set({ isLoadingMembers: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.get<OrganizationMember[]>(`/organizations/${org.id}/members`);
          set({ currentOrgMembers: response.data, isLoadingMembers: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to load members',
            isLoadingMembers: false
          });
          throw error;
        }
      },

      loadSelectedOrgMembers: async (orgId) => {
        set({ isLoadingMembers: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.get<OrganizationMember[]>(`/organizations/${orgId}/members`);
          set({ selectedOrgMembers: response.data, isLoadingMembers: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to load members',
            isLoadingMembers: false
          });
          throw error;
        }
      },

      updateMemberRole: async (orgId, userId, data) => {
        set({ isLoadingMembers: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          await apiClient.patch(`/organizations/${orgId}/members/${userId}`, data);

          // Reload members
          if (get().currentOrganization?.id === orgId) {
            await get().loadCurrentOrgMembers();
          } else {
            await get().loadSelectedOrgMembers(orgId);
          }
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to update member role',
            isLoadingMembers: false
          });
          throw error;
        }
      },

      removeMember: async (orgId, userId) => {
        set({ isLoadingMembers: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          await apiClient.delete(`/organizations/${orgId}/members/${userId}`);

          // Remove from local state
          if (get().currentOrganization?.id === orgId) {
            set({
              currentOrgMembers: get().currentOrgMembers.filter(m => m.user_id !== userId),
              isLoadingMembers: false
            });
          } else {
            set({
              selectedOrgMembers: get().selectedOrgMembers.filter(m => m.user_id !== userId),
              isLoadingMembers: false
            });
          }
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to remove member',
            isLoadingMembers: false
          });
          throw error;
        }
      },

      // Department Management
      loadCurrentOrgDepartments: async () => {
        const org = get().currentOrganization;
        if (!org) return;

        set({ isLoadingDepartments: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.get<Department[]>(`/organizations/${org.id}/departments`);
          set({ currentOrgDepartments: response.data, isLoadingDepartments: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to load departments',
            isLoadingDepartments: false
          });
          throw error;
        }
      },

      loadSelectedOrgDepartments: async (orgId) => {
        set({ isLoadingDepartments: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.get<Department[]>(`/organizations/${orgId}/departments`);
          set({ selectedOrgDepartments: response.data, isLoadingDepartments: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to load departments',
            isLoadingDepartments: false
          });
          throw error;
        }
      },

      createDepartment: async (orgId, data) => {
        set({ isLoadingDepartments: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.post<Department>(`/organizations/${orgId}/departments`, data);
          const newDept = response.data;

          // Add to current org departments if applicable
          if (get().currentOrganization?.id === orgId) {
            set({
              currentOrgDepartments: [...get().currentOrgDepartments, newDept],
              isLoadingDepartments: false
            });
          } else {
            set({ isLoadingDepartments: false });
          }

          return newDept;
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to create department',
            isLoadingDepartments: false
          });
          throw error;
        }
      },

      // Invitation Management
      sendInvitation: async (orgId, data) => {
        set({ isLoading: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.post<OrganizationInvite>(`/organizations/${orgId}/invites`, data);
          set({ isLoading: false });
          return response.data;
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to send invitation',
            isLoading: false
          });
          throw error;
        }
      },

      acceptInvitation: async (token) => {
        set({ isLoading: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.post<{ organization_id: string; role: string; message: string }>(`/invites/${token}/accept`);

          // Load the organization user just joined
          const orgId = response.data.organization_id;
          const org = await get().getOrganization(orgId);
          set({ currentOrganization: org, isLoading: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to accept invitation',
            isLoading: false
          });
          throw error;
        }
      },

      // Investigation Management
      loadCurrentOrgInvestigations: async () => {
        const org = get().currentOrganization;
        if (!org) return;

        set({ isLoadingInvestigations: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          // TODO: This endpoint doesn't exist yet - would need to add to backend
          // For now, just clear the loading state
          set({ currentOrgInvestigations: [], isLoadingInvestigations: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to load investigations',
            isLoadingInvestigations: false
          });
          throw error;
        }
      },

      createInvestigation: async (data) => {
        set({ isLoadingInvestigations: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.post<InvestigationThread>('/investigations', data);
          const newInvestigation = response.data;

          // Add to current investigations if same org
          if (get().currentOrganization?.id === data.organization_id) {
            set({
              currentOrgInvestigations: [...get().currentOrgInvestigations, newInvestigation],
              isLoadingInvestigations: false
            });
          } else {
            set({ isLoadingInvestigations: false });
          }

          return newInvestigation;
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to create investigation',
            isLoadingInvestigations: false
          });
          throw error;
        }
      },

      updateInvestigation: async (id, data) => {
        set({ isLoadingInvestigations: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.patch<InvestigationThread>(`/investigations/${id}`, data);
          const updatedInvestigation = response.data;

          // Update in current investigations
          set({
            currentOrgInvestigations: get().currentOrgInvestigations.map(inv =>
              inv.id === id ? updatedInvestigation : inv
            ),
            isLoadingInvestigations: false
          });

          return updatedInvestigation;
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to update investigation',
            isLoadingInvestigations: false
          });
          throw error;
        }
      },

      publishInvestigation: async (id) => {
        set({ isLoadingInvestigations: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          const response = await apiClient.post<InvestigationThread>(`/investigations/${id}/publish`);
          const publishedInvestigation = response.data;

          // Update in current investigations
          set({
            currentOrgInvestigations: get().currentOrgInvestigations.map(inv =>
              inv.id === id ? publishedInvestigation : inv
            ),
            isLoadingInvestigations: false
          });

          return publishedInvestigation;
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to publish investigation',
            isLoadingInvestigations: false
          });
          throw error;
        }
      },

      deleteInvestigation: async (id) => {
        set({ isLoadingInvestigations: true, error: null });
        try {
          const { apiClient } = await import('@/lib/api-client');
          await apiClient.delete(`/investigations/${id}`);

          // Remove from current investigations
          set({
            currentOrgInvestigations: get().currentOrgInvestigations.filter(inv => inv.id !== id),
            isLoadingInvestigations: false
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.error?.message || 'Failed to delete investigation',
            isLoadingInvestigations: false
          });
          throw error;
        }
      },

      // Utility
      clearError: () => {
        set({ error: null });
      },

      reset: () => {
        set(initialState);
      },
    }),
    {
      name: 'receipts-organization',
      partialize: (state) => ({
        currentOrganization: state.currentOrganization,
        organizations: state.organizations,
        currentOrgDepartments: state.currentOrgDepartments,
      }),
    }
  )
);

// Hook to initialize organization data when user is authenticated
export function useOrganizationInit() {
  const { loadOrganizationList, setCurrentOrganization } = useOrganizationStore();

  const initOrganization = async (user: any) => {
    // If user has an organization, set it as current
    if (user?.organization_id && user?.organization_slug && user?.organization_name) {
      setCurrentOrganization({
        id: user.organization_id,
        slug: user.organization_slug,
        name: user.organization_name,
        description: null,
        logo_url: null,
        website_url: null,
        is_verified: user.is_verified_newsroom_member || false,
        member_count: 0,
        created_at: new Date().toISOString(),
      });
    }

    // Load organization directory (cached)
    try {
      await loadOrganizationList();
    } catch (error) {
      // Fail silently - not critical for app initialization
      console.error('Failed to load organization directory:', error);
    }
  };

  return initOrganization;
}

// Selector hooks for common use cases
export const useCurrentOrganization = () =>
  useOrganizationStore((state) => state.currentOrganization);

export const useIsOrgMember = () =>
  useOrganizationStore((state) => !!state.currentOrganization);

export const useIsOrgAdmin = () =>
  useOrganizationStore((state) => {
    // Would need to check user's role in the organization
    // This is a placeholder - actual implementation would check UserPrivate.organization_role
    return false;
  });

export const useOrganizations = () =>
  useOrganizationStore((state) => state.organizations);

export const useCurrentOrgMembers = () =>
  useOrganizationStore((state) => state.currentOrgMembers);

export const useCurrentOrgDepartments = () =>
  useOrganizationStore((state) => state.currentOrgDepartments);
