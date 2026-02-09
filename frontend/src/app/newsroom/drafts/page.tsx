'use client';

import { useRouter } from 'next/navigation';
import { FileText, Plus } from 'lucide-react';
import { RequireAuth } from '@/components/auth';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useCurrentOrganization } from '@/state/organization-store';

export default function DraftsPage() {
  return (
    <RequireAuth>
      <DraftsContent />
    </RequireAuth>
  );
}

function DraftsContent() {
  const router = useRouter();
  const currentOrg = useCurrentOrganization();

  if (!currentOrg) {
    return (
      <div className="container mx-auto px-4 py-12 text-center max-w-2xl">
        <FileText className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
        <h2 className="text-2xl font-bold mb-4">Not a Newsroom Member</h2>
        <p className="text-muted-foreground mb-6">
          You need to be part of a newsroom to access drafts.
        </p>
        <Button onClick={() => router.push('/newsroom')}>
          Browse Newsrooms
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <FileText className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold">Drafts</h1>
          </div>
          <Button onClick={() => router.push('/create')}>
            <Plus className="h-4 w-4 mr-2" />
            New Receipt
          </Button>
        </div>
        <p className="text-muted-foreground">
          Collaborative workspace for {currentOrg.name}
        </p>
      </div>

      {/* Drafts List Placeholder */}
      <Card className="p-12 text-center">
        <FileText className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
        <h3 className="text-lg font-semibold mb-2">No Drafts Yet</h3>
        <p className="text-muted-foreground mb-6">
          Start creating receipts to see them here before publishing.
        </p>
        <Button variant="outline" onClick={() => router.push('/create')}>
          Create Your First Receipt
        </Button>
      </Card>
    </div>
  );
}
