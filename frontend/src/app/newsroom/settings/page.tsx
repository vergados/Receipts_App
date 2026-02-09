'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { Settings as SettingsIcon, Save } from 'lucide-react';
import { RequireAuth } from '@/components/auth';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  useCurrentOrganization,
  useOrganizationStore,
} from '@/state/organization-store';
import { useAuthStore } from '@/state/auth-store';
import { toast } from 'sonner';

export default function SettingsPage() {
  return (
    <RequireAuth>
      <SettingsContent />
    </RequireAuth>
  );
}

function SettingsContent() {
  const router = useRouter();
  const { user } = useAuthStore();
  const currentOrg = useCurrentOrganization();
  const { updateOrganization, isLoading } = useOrganizationStore();

  const [name, setName] = useState(currentOrg?.name || '');
  const [description, setDescription] = useState(currentOrg?.description || '');
  const [websiteUrl, setWebsiteUrl] = useState(currentOrg?.website_url || '');

  const isAdmin = user?.organization_role === 'admin';

  if (!currentOrg) {
    return (
      <div className="container mx-auto px-4 py-12 text-center max-w-2xl">
        <SettingsIcon className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
        <h2 className="text-2xl font-bold mb-4">Not a Newsroom Member</h2>
        <p className="text-muted-foreground mb-6">
          You need to be part of a newsroom to access settings.
        </p>
        <Button onClick={() => router.push('/newsroom')}>
          Browse Newsrooms
        </Button>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="container mx-auto px-4 py-12 text-center max-w-2xl">
        <SettingsIcon className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
        <h2 className="text-2xl font-bold mb-4">Permission Denied</h2>
        <p className="text-muted-foreground mb-6">
          Only organization admins can access settings.
        </p>
        <Button onClick={() => router.push('/newsroom/dashboard')}>
          Back to Dashboard
        </Button>
      </div>
    );
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    try {
      await updateOrganization(currentOrg.id, {
        name: name !== currentOrg.name ? name : undefined,
        description: description !== currentOrg.description ? description : undefined,
        website_url: websiteUrl !== currentOrg.website_url ? websiteUrl : undefined,
      });

      toast.success('Settings updated successfully');
    } catch (err) {
      toast.error('Failed to update settings');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <SettingsIcon className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Organization Settings</h1>
        </div>
        <p className="text-muted-foreground">
          Manage settings for {currentOrg.name}
        </p>
      </div>

      {/* Settings Form */}
      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Organization Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium mb-2">
              Organization Name
            </label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. New York Times"
              required
              disabled={isLoading}
            />
            <p className="text-xs text-muted-foreground mt-1">
              The public name of your organization
            </p>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium mb-2">
              Description
            </label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of your newsroom..."
              rows={4}
              disabled={isLoading}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Appears on your public profile
            </p>
          </div>

          {/* Website URL */}
          <div>
            <label htmlFor="website" className="block text-sm font-medium mb-2">
              Website URL
            </label>
            <Input
              id="website"
              type="url"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              placeholder="https://example.com"
              disabled={isLoading}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Link to your organization's website
            </p>
          </div>

          {/* Read-only fields */}
          <div className="border-t pt-6 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-muted-foreground">
                Organization Slug (Read-only)
              </label>
              <Input value={currentOrg.slug} disabled />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-muted-foreground">
                Verification Status
              </label>
              <div className="flex items-center gap-2">
                <Input
                  value={currentOrg.is_verified ? 'Verified' : 'Not Verified'}
                  disabled
                  className="flex-1"
                />
                {!currentOrg.is_verified && (
                  <p className="text-xs text-muted-foreground">
                    Contact support for verification
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push('/newsroom/dashboard')}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>Saving...</>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
