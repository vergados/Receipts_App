'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Mail, CheckCircle, AlertCircle } from 'lucide-react';
import { RequireAuth } from '@/components/auth';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import { useOrganizationStore } from '@/state/organization-store';
import { useAuthStore } from '@/state/auth-store';

export default function AcceptInvitePage() {
  return (
    <RequireAuth>
      <AcceptInviteContent />
    </RequireAuth>
  );
}

function AcceptInviteContent() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  const { user } = useAuthStore();
  const { acceptInvitation, isLoading, error, clearError } = useOrganizationStore();

  const [accepting, setAccepting] = useState(false);
  const [accepted, setAccepted] = useState(false);

  useEffect(() => {
    clearError();
  }, []);

  const handleAccept = async () => {
    if (!token) return;

    setAccepting(true);
    try {
      await acceptInvitation(token);
      setAccepted(true);

      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        router.push('/newsroom/dashboard');
      }, 2000);
    } catch (err) {
      // Error handled by store
      setAccepting(false);
    }
  };

  if (!token) {
    return (
      <div className="container mx-auto px-4 py-12 text-center max-w-2xl">
        <AlertCircle className="h-16 w-16 mx-auto text-destructive mb-4" />
        <h2 className="text-2xl font-bold mb-4">Invalid Invitation</h2>
        <p className="text-muted-foreground mb-6">
          This invitation link is not valid.
        </p>
        <Button onClick={() => router.push('/newsroom')}>
          Browse Newsrooms
        </Button>
      </div>
    );
  }

  if (accepted) {
    return (
      <div className="container mx-auto px-4 py-12 text-center max-w-2xl">
        <Card className="p-12">
          <CheckCircle className="h-16 w-16 mx-auto text-green-600 dark:text-green-400 mb-4" />
          <h2 className="text-2xl font-bold mb-4">Welcome to the Team!</h2>
          <p className="text-muted-foreground mb-6">
            You've successfully joined the organization.
          </p>
          <p className="text-sm text-muted-foreground">
            Redirecting to your newsroom dashboard...
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12 max-w-2xl">
      <Card className="p-12 text-center">
        <Mail className="h-16 w-16 mx-auto text-primary mb-4" />

        <h1 className="text-3xl font-bold mb-4">You've Been Invited!</h1>

        <p className="text-muted-foreground mb-8">
          You've been invited to join a newsroom organization on Receipts.
          {user && (
            <span className="block mt-2">
              You're logged in as <strong>{user.display_name}</strong> (@{user.handle})
            </span>
          )}
        </p>

        {error && (
          <div className="mb-6 p-4 bg-destructive/10 text-destructive rounded-md text-sm flex items-start gap-2">
            <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
            <div className="text-left">
              <p className="font-medium mb-1">Unable to Accept Invitation</p>
              <p>{error}</p>
              {error.includes('expired') && (
                <p className="mt-2 text-xs">
                  Please contact your organization admin for a new invitation.
                </p>
              )}
            </div>
          </div>
        )}

        <div className="flex flex-col gap-3">
          <Button
            size="lg"
            onClick={handleAccept}
            disabled={accepting || isLoading}
            className="w-full"
          >
            {accepting ? (
              <>
                <Spinner size="sm" className="mr-2" />
                Accepting Invitation...
              </>
            ) : (
              <>Accept Invitation</>
            )}
          </Button>

          <Button
            variant="outline"
            onClick={() => router.push('/newsroom')}
            disabled={accepting || isLoading}
          >
            Cancel
          </Button>
        </div>

        <p className="text-xs text-muted-foreground mt-6">
          By accepting, you'll become a member of this organization and gain access
          to collaborative newsroom features.
        </p>
      </Card>
    </div>
  );
}
