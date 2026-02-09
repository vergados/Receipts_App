'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Users, Folder } from 'lucide-react';
import { NewsroomHeader } from '@/components/newsroom';
import { useOrganizationStore, useCurrentOrganization } from '@/state/organization-store';
import { useAuthStore } from '@/state/auth-store';
import { Spinner } from '@/components/ui/spinner';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Organization } from '@/lib/types';

export default function OrganizationProfilePage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;

  const { user } = useAuthStore();
  const currentOrg = useCurrentOrganization();
  const {
    getOrganization,
    loadSelectedOrgMembers,
    loadSelectedOrgDepartments,
    selectedOrgMembers,
    selectedOrgDepartments,
    isLoading,
    isLoadingMembers,
    isLoadingDepartments,
    error,
  } = useOrganizationStore();

  const [organization, setOrganization] = useState<Organization | null>(null);

  useEffect(() => {
    const loadOrg = async () => {
      try {
        const org = await getOrganization(slug);
        setOrganization(org);

        // Load members and departments
        loadSelectedOrgMembers(org.id);
        loadSelectedOrgDepartments(org.id);
      } catch (err) {
        // Error handled by store
      }
    };

    loadOrg();
  }, [slug]);

  const isAdmin = user && currentOrg?.id === organization?.id && user.organization_role === 'admin';

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !organization) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold mb-4">Organization Not Found</h2>
        <p className="text-muted-foreground mb-6">
          The organization you're looking for doesn't exist or has been removed.
        </p>
        <button
          onClick={() => router.push('/newsroom')}
          className="text-primary hover:underline"
        >
          Browse all newsrooms
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <NewsroomHeader
        organization={organization}
        isAdmin={isAdmin}
        onSettingsClick={() => router.push('/newsroom/settings')}
      />

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* About */}
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">About</h2>
              {organization.description ? (
                <p className="text-muted-foreground">{organization.description}</p>
              ) : (
                <p className="text-muted-foreground italic">No description provided.</p>
              )}
            </Card>

            {/* Recent Receipts - TODO: Add when receipts are filtered by org */}
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Recent Receipts</h2>
              <p className="text-muted-foreground text-sm">
                Organization receipts will appear here.
              </p>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Departments */}
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <Folder className="h-5 w-5 text-primary" />
                <h3 className="font-semibold">Departments</h3>
              </div>

              {isLoadingDepartments ? (
                <Spinner size="sm" />
              ) : selectedOrgDepartments.length > 0 ? (
                <div className="space-y-2">
                  {selectedOrgDepartments.map((dept) => (
                    <div
                      key={dept.id}
                      className="flex items-center justify-between text-sm"
                    >
                      <span>{dept.name}</span>
                      <Badge variant="secondary" className="text-xs">
                        {dept.member_count}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No departments</p>
              )}
            </Card>

            {/* Team Preview */}
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <Users className="h-5 w-5 text-primary" />
                <h3 className="font-semibold">Team</h3>
              </div>

              {isLoadingMembers ? (
                <Spinner size="sm" />
              ) : (
                <div className="space-y-3">
                  <div className="text-sm text-muted-foreground">
                    {selectedOrgMembers.length}{' '}
                    {selectedOrgMembers.length === 1 ? 'member' : 'members'}
                  </div>

                  {/* Show first 5 members */}
                  {selectedOrgMembers.slice(0, 5).map((member) => (
                    <div key={member.user_id} className="flex items-center gap-2">
                      <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-medium">
                        {member.display_name.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {member.display_name}
                        </p>
                        <p className="text-xs text-muted-foreground truncate">
                          @{member.handle}
                        </p>
                      </div>
                    </div>
                  ))}

                  {selectedOrgMembers.length > 5 && (
                    <p className="text-xs text-muted-foreground">
                      +{selectedOrgMembers.length - 5} more
                    </p>
                  )}
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
