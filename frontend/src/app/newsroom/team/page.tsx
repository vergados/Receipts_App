'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Users } from 'lucide-react';
import { RequireAuth } from '@/components/auth';
import { TeamRoster, InviteForm, DeskManager } from '@/components/newsroom';
import {
  useCurrentOrganization,
  useCurrentOrgMembers,
  useCurrentOrgDepartments,
  useOrganizationStore,
} from '@/state/organization-store';
import { useAuthStore } from '@/state/auth-store';
import { Spinner } from '@/components/ui/spinner';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

export default function TeamManagementPage() {
  return (
    <RequireAuth>
      <TeamManagementContent />
    </RequireAuth>
  );
}

function TeamManagementContent() {
  const router = useRouter();
  const { user } = useAuthStore();
  const currentOrg = useCurrentOrganization();
  const members = useCurrentOrgMembers();
  const departments = useCurrentOrgDepartments();
  const {
    loadCurrentOrgMembers,
    loadCurrentOrgDepartments,
    updateMemberRole,
    removeMember,
    createDepartment,
    isLoading,
    isLoadingMembers,
  } = useOrganizationStore();

  useEffect(() => {
    if (currentOrg) {
      loadCurrentOrgMembers();
      loadCurrentOrgDepartments();
    }
  }, [currentOrg?.id]);

  // Check permissions (admin or editor)
  const isAdmin = user?.organization_role === 'admin';
  const isEditor = user?.organization_role === 'editor';
  const canManage = isAdmin || isEditor;

  if (!isLoading && !currentOrg) {
    return (
      <div className="container mx-auto px-4 py-12 text-center max-w-2xl">
        <Users className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
        <h2 className="text-2xl font-bold mb-4">Not a Newsroom Member</h2>
        <p className="text-muted-foreground mb-6">
          You need to be part of a newsroom to manage team members.
        </p>
        <Button onClick={() => router.push('/newsroom')}>
          Browse Newsrooms
        </Button>
      </div>
    );
  }

  if (!canManage && currentOrg) {
    return (
      <div className="container mx-auto px-4 py-12 text-center max-w-2xl">
        <Users className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
        <h2 className="text-2xl font-bold mb-4">Permission Denied</h2>
        <p className="text-muted-foreground mb-6">
          Only admins and editors can manage team members.
        </p>
        <Button onClick={() => router.push('/newsroom/dashboard')}>
          Back to Dashboard
        </Button>
      </div>
    );
  }

  if (isLoading || !currentOrg) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  const handleRoleChange = async (userId: string, newRole: any) => {
    try {
      await updateMemberRole(currentOrg.id, userId, { role: newRole });
      toast.success('Member role updated');
    } catch (err) {
      toast.error('Failed to update role');
    }
  };

  const handleRemoveMember = async (userId: string) => {
    try {
      await removeMember(currentOrg.id, userId);
      toast.success('Member removed');
    } catch (err) {
      toast.error('Failed to remove member');
    }
  };

  const handleCreateDepartment = async (data: {
    name: string;
    description?: string;
  }) => {
    try {
      await createDepartment(currentOrg.id, data);
      toast.success('Department created');
    } catch (err) {
      toast.error('Failed to create department');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <Users className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Team Management</h1>
        </div>
        <p className="text-muted-foreground">
          Manage team members and departments for {currentOrg.name}
        </p>
      </div>

      <div className="space-y-8">
        {/* Invite Form */}
        {canManage && (
          <InviteForm
            organizationId={currentOrg.id}
            departments={departments}
            onSuccess={() => {
              toast.success('Invitation sent!');
            }}
          />
        )}

        {/* Team Roster */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Team Members</h2>
          {isLoadingMembers ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : (
            <TeamRoster
              members={members}
              isAdmin={canManage}
              onRoleChange={handleRoleChange}
              onRemoveMember={handleRemoveMember}
            />
          )}
        </div>

        {/* Department Management */}
        {isAdmin && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Departments</h2>
            <DeskManager
              departments={departments}
              onCreateDepartment={handleCreateDepartment}
              isLoading={isLoading}
            />
          </div>
        )}
      </div>
    </div>
  );
}
