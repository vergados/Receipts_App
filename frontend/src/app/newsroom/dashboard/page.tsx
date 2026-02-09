'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  Users,
  FileText,
  TrendingUp,
  Settings,
  Folder,
} from 'lucide-react';
import { RequireAuth } from '@/components/auth';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  useCurrentOrganization,
  useCurrentOrgMembers,
  useCurrentOrgDepartments,
  useOrganizationStore,
} from '@/state/organization-store';
import { useAuthStore } from '@/state/auth-store';
import { Spinner } from '@/components/ui/spinner';
import { formatNumber } from '@/lib/utils';

export default function NewsroomDashboardPage() {
  return (
    <RequireAuth>
      <DashboardContent />
    </RequireAuth>
  );
}

function DashboardContent() {
  const router = useRouter();
  const { user } = useAuthStore();
  const currentOrg = useCurrentOrganization();
  const members = useCurrentOrgMembers();
  const departments = useCurrentOrgDepartments();
  const { loadCurrentOrgMembers, loadCurrentOrgDepartments, isLoading } =
    useOrganizationStore();

  useEffect(() => {
    if (currentOrg) {
      loadCurrentOrgMembers();
      loadCurrentOrgDepartments();
    }
  }, [currentOrg?.id]);

  // Redirect if not a member
  if (!isLoading && !currentOrg) {
    return (
      <div className="container mx-auto px-4 py-12 text-center max-w-2xl">
        <LayoutDashboard className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
        <h2 className="text-2xl font-bold mb-4">Not a Newsroom Member</h2>
        <p className="text-muted-foreground mb-6">
          You need to be part of a verified newsroom organization to access this dashboard.
        </p>
        <Button onClick={() => router.push('/newsroom')}>
          Browse Newsrooms
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

  const isAdmin = user?.organization_role === 'admin';
  const isEditor = user?.organization_role === 'editor' || isAdmin;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back to {currentOrg.name}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <Users className="h-8 w-8 text-primary" />
            <Badge variant="secondary">Team</Badge>
          </div>
          <p className="text-3xl font-bold mb-1">{formatNumber(members.length)}</p>
          <p className="text-sm text-muted-foreground">Team members</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <Folder className="h-8 w-8 text-primary" />
            <Badge variant="secondary">Desks</Badge>
          </div>
          <p className="text-3xl font-bold mb-1">{formatNumber(departments.length)}</p>
          <p className="text-sm text-muted-foreground">Departments</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <FileText className="h-8 w-8 text-primary" />
            <Badge variant="secondary">Content</Badge>
          </div>
          <p className="text-3xl font-bold mb-1">0</p>
          <p className="text-sm text-muted-foreground">Receipts published</p>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button
            variant="outline"
            className="h-auto py-6 flex-col gap-2"
            onClick={() => router.push('/create')}
          >
            <FileText className="h-6 w-6" />
            <span>New Receipt</span>
          </Button>

          {isEditor && (
            <Button
              variant="outline"
              className="h-auto py-6 flex-col gap-2"
              onClick={() => router.push('/newsroom/team')}
            >
              <Users className="h-6 w-6" />
              <span>Manage Team</span>
            </Button>
          )}

          <Button
            variant="outline"
            className="h-auto py-6 flex-col gap-2"
            onClick={() => router.push('/newsroom/analytics')}
          >
            <TrendingUp className="h-6 w-6" />
            <span>Analytics</span>
          </Button>

          {isAdmin && (
            <Button
              variant="outline"
              className="h-auto py-6 flex-col gap-2"
              onClick={() => router.push('/newsroom/settings')}
            >
              <Settings className="h-6 w-6" />
              <span>Settings</span>
            </Button>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <div className="text-center py-8 text-muted-foreground">
          <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p>No recent activity</p>
          <p className="text-sm">Activity from your newsroom will appear here</p>
        </div>
      </Card>
    </div>
  );
}
