'use client';

import { useRouter } from 'next/navigation';
import { TrendingUp, Eye, Heart, MessageCircle, Users } from 'lucide-react';
import { RequireAuth } from '@/components/auth';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useCurrentOrganization } from '@/state/organization-store';
import { Spinner } from '@/components/ui/spinner';

export default function AnalyticsPage() {
  return (
    <RequireAuth>
      <AnalyticsContent />
    </RequireAuth>
  );
}

function AnalyticsContent() {
  const router = useRouter();
  const currentOrg = useCurrentOrganization();

  if (!currentOrg) {
    return (
      <div className="container mx-auto px-4 py-12 text-center max-w-2xl">
        <TrendingUp className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
        <h2 className="text-2xl font-bold mb-4">Not a Newsroom Member</h2>
        <p className="text-muted-foreground mb-6">
          You need to be part of a newsroom to view analytics.
        </p>
        <Button onClick={() => router.push('/newsroom')}>
          Browse Newsrooms
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <TrendingUp className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Analytics</h1>
        </div>
        <p className="text-muted-foreground">
          Performance metrics for {currentOrg.name}
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <Eye className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Views</h3>
          </div>
          <p className="text-3xl font-bold">0</p>
          <p className="text-xs text-muted-foreground mt-1">Last 30 days</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <Heart className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Engagement</h3>
          </div>
          <p className="text-3xl font-bold">0</p>
          <p className="text-xs text-muted-foreground mt-1">Reactions & shares</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <MessageCircle className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Receipts</h3>
          </div>
          <p className="text-3xl font-bold">0</p>
          <p className="text-xs text-muted-foreground mt-1">Published</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <Users className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-sm font-medium text-muted-foreground">Reach</h3>
          </div>
          <p className="text-3xl font-bold">0</p>
          <p className="text-xs text-muted-foreground mt-1">Unique viewers</p>
        </Card>
      </div>

      {/* Charts Placeholder */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Performance Over Time</h2>
        <div className="text-center py-12 text-muted-foreground">
          <TrendingUp className="h-16 w-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium mb-2">Analytics Coming Soon</p>
          <p className="text-sm">
            Detailed analytics and insights will be available once you start publishing.
          </p>
        </div>
      </Card>
    </div>
  );
}
