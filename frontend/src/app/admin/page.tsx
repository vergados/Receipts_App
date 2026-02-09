'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Shield, Users, Flag, History, BarChart3, AlertTriangle,
  CheckCircle, XCircle, Ban, Loader2, Search, ChevronRight
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { RequireAuth } from '@/components/auth';
import { useAuthStore } from '@/state/auth-store';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Spinner } from '@/components/ui/spinner';
import { cn, formatRelativeTime } from '@/lib/utils';
import type {
  AdminStats, AdminReport, AdminReportList, AdminUser, AdminUserList,
  ModerationAction, ModerationActionList, ReportStatus, ModerationActionType
} from '@/lib/types';

type Tab = 'overview' | 'reports' | 'users' | 'actions';

const reportStatusColors: Record<ReportStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  reviewed: 'bg-blue-100 text-blue-800',
  actioned: 'bg-green-100 text-green-800',
  dismissed: 'bg-gray-100 text-gray-800',
};

const actionTypeLabels: Record<ModerationActionType, string> = {
  warning: 'Warning',
  content_removal: 'Content Removed',
  user_ban: 'User Banned',
  user_suspension: 'User Suspended',
};

function StatCard({ title, value, icon: Icon, color }: {
  title: string;
  value: number;
  icon: React.ElementType;
  color: string;
}) {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        <div className={cn('p-3 rounded-full', color)}>
          <Icon className="h-5 w-5 text-white" />
        </div>
      </div>
    </Card>
  );
}

function OverviewTab({ stats }: { stats: AdminStats | undefined }) {
  if (!stats) return <Spinner />;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Users" value={stats.total_users} icon={Users} color="bg-blue-500" />
        <StatCard title="Total Receipts" value={stats.total_receipts} icon={BarChart3} color="bg-green-500" />
        <StatCard title="Pending Reports" value={stats.pending_reports} icon={Flag} color="bg-yellow-500" />
        <StatCard title="Actions Today" value={stats.actions_today} icon={History} color="bg-purple-500" />
      </div>

      {stats.pending_reports > 0 && (
        <Card className="p-4 border-yellow-200 bg-yellow-50">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600" />
            <div>
              <p className="font-medium text-yellow-800">Attention Required</p>
              <p className="text-sm text-yellow-700">
                You have {stats.pending_reports} pending report{stats.pending_reports !== 1 ? 's' : ''} to review.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

function ReportsTab() {
  const queryClient = useQueryClient();
  const [selectedReport, setSelectedReport] = useState<AdminReport | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'reports'],
    queryFn: async () => {
      const res = await apiClient.get<AdminReportList>('/admin/reports?limit=50');
      return res.data;
    },
  });

  const reviewMutation = useMutation({
    mutationFn: async ({ reportId, status, actionType, actionReason }: {
      reportId: string;
      status: ReportStatus;
      actionType?: ModerationActionType;
      actionReason?: string;
    }) => {
      await apiClient.post(`/admin/reports/${reportId}/review`, {
        status,
        action_type: actionType,
        action_reason: actionReason,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin'] });
      setSelectedReport(null);
      toast.success('Report reviewed');
    },
  });

  const handleReview = (reportId: string, status: ReportStatus, actionType?: ModerationActionType) => {
    reviewMutation.mutate({
      reportId,
      status,
      actionType,
      actionReason: actionType ? `Action taken: ${actionTypeLabels[actionType]}` : undefined,
    });
  };

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-medium">Reports ({data?.total || 0})</h3>
        <Badge variant="secondary">
          {data?.pending_count || 0} pending
        </Badge>
      </div>

      {data?.reports.length === 0 ? (
        <Card className="p-8 text-center">
          <Flag className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No reports yet</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {data?.reports.map((report) => (
            <Card
              key={report.id}
              className={cn(
                'p-4 cursor-pointer hover:shadow-md transition-shadow',
                report.status === 'pending' && 'border-yellow-200'
              )}
              onClick={() => setSelectedReport(report)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className={reportStatusColors[report.status]}>
                      {report.status}
                    </Badge>
                    <span className="text-sm font-medium capitalize">{report.reason.replace('_', ' ')}</span>
                    <span className="text-xs text-muted-foreground">
                      {formatRelativeTime(report.created_at)}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-1">
                    Reported by @{report.reporter.handle}
                  </p>
                  {report.target_user && (
                    <p className="text-sm">
                      User: <span className="font-medium">@{report.target_user.handle}</span>
                      {!report.target_user.is_active && (
                        <Badge variant="destructive" className="ml-2 text-xs">Banned</Badge>
                      )}
                    </p>
                  )}
                  {report.target_receipt && (
                    <p className="text-sm truncate">
                      Receipt: "{report.target_receipt.claim_text}"
                    </p>
                  )}
                </div>
                <ChevronRight className="h-5 w-5 text-muted-foreground" />
              </div>

              {report.status === 'pending' && (
                <div className="flex gap-2 mt-3 pt-3 border-t" onClick={(e) => e.stopPropagation()}>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleReview(report.id, 'dismissed')}
                    disabled={reviewMutation.isPending}
                  >
                    <XCircle className="h-4 w-4 mr-1" />
                    Dismiss
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleReview(report.id, 'actioned', 'warning')}
                    disabled={reviewMutation.isPending}
                  >
                    <AlertTriangle className="h-4 w-4 mr-1" />
                    Warn
                  </Button>
                  {report.target_type === 'receipt' && (
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleReview(report.id, 'actioned', 'content_removal')}
                      disabled={reviewMutation.isPending}
                    >
                      Remove Content
                    </Button>
                  )}
                  {report.target_type === 'user' && (
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleReview(report.id, 'actioned', 'user_ban')}
                      disabled={reviewMutation.isPending}
                    >
                      <Ban className="h-4 w-4 mr-1" />
                      Ban User
                    </Button>
                  )}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function UsersTab() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'users', search],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: '50' });
      if (search) params.set('search', search);
      const res = await apiClient.get<AdminUserList>(`/admin/users?${params}`);
      return res.data;
    },
  });

  const toggleStatusMutation = useMutation({
    mutationFn: async (userId: string) => {
      await apiClient.post(`/admin/users/${userId}/toggle-status`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
      toast.success('User status updated');
    },
  });

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input
          type="search"
          placeholder="Search users..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-10 w-full rounded-md border border-input bg-background pl-10 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      <div className="space-y-3">
        {data?.users.map((user) => (
          <Card key={user.id} className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Avatar src={user.avatar_url} fallback={user.display_name} size="lg" />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{user.display_name}</span>
                    {user.is_moderator && (
                      <Badge variant="secondary" className="text-xs">
                        <Shield className="h-3 w-3 mr-1" />
                        Mod
                      </Badge>
                    )}
                    {!user.is_active && (
                      <Badge variant="destructive" className="text-xs">Banned</Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">@{user.handle}</p>
                  <p className="text-xs text-muted-foreground">{user.email}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm">{user.receipt_count} receipts</p>
                {user.report_count > 0 && (
                  <p className="text-xs text-destructive">{user.report_count} reports</p>
                )}
                <Button
                  size="sm"
                  variant={user.is_active ? 'destructive' : 'outline'}
                  className="mt-2"
                  onClick={() => toggleStatusMutation.mutate(user.id)}
                  disabled={toggleStatusMutation.isPending || user.is_moderator}
                >
                  {toggleStatusMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : user.is_active ? (
                    <>
                      <Ban className="h-4 w-4 mr-1" />
                      Ban
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Unban
                    </>
                  )}
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function ActionsTab() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'actions'],
    queryFn: async () => {
      const res = await apiClient.get<ModerationActionList>('/admin/actions?limit=50');
      return res.data;
    },
  });

  if (isLoading) return <Spinner />;

  return (
    <div className="space-y-4">
      <h3 className="font-medium">Action History ({data?.total || 0})</h3>

      {data?.actions.length === 0 ? (
        <Card className="p-8 text-center">
          <History className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No moderation actions yet</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {data?.actions.map((action) => (
            <Card key={action.id} className="p-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="secondary">
                      {actionTypeLabels[action.action_type]}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {formatRelativeTime(action.created_at)}
                    </span>
                  </div>
                  <p className="text-sm">{action.reason}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    By @{action.moderator.handle} · Target: {action.target_type} ({action.target_id.slice(0, 8)}...)
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function AdminContent() {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<Tab>('overview');

  const { data: stats } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: async () => {
      const res = await apiClient.get<AdminStats>('/admin/stats');
      return res.data;
    },
    enabled: !!user?.is_moderator,
  });

  const tabs: { id: Tab; label: string; icon: React.ElementType }[] = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'reports', label: 'Reports', icon: Flag },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'actions', label: 'Actions', icon: History },
  ];

  return (
    <div className="container mx-auto px-4 py-6 max-w-4xl">
      <div className="flex items-center gap-3 mb-6">
        <Shield className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground">Manage reports, users, and moderation</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
              activeTab === tab.id
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            )}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
            {tab.id === 'reports' && stats && stats.pending_reports > 0 && (
              <Badge variant="destructive" className="ml-1 h-5 px-1.5 text-xs">
                {stats.pending_reports}
              </Badge>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab stats={stats} />}
      {activeTab === 'reports' && <ReportsTab />}
      {activeTab === 'users' && <UsersTab />}
      {activeTab === 'actions' && <ActionsTab />}
    </div>
  );
}

export default function AdminPage() {
  return (
    <RequireAuth requireModerator>
      <AdminContent />
    </RequireAuth>
  );
}
