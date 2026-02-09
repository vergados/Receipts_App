'use client';

import { Building2, ExternalLink, Users } from 'lucide-react';
import type { Organization } from '@/lib/types';
import { VerifiedBadge } from './verified-badge';
import { Button } from '@/components/ui/button';
import { formatNumber } from '@/lib/utils';

interface NewsroomHeaderProps {
  organization: Organization;
  isAdmin?: boolean;
  onSettingsClick?: () => void;
}

export function NewsroomHeader({
  organization,
  isAdmin = false,
  onSettingsClick,
}: NewsroomHeaderProps) {
  return (
    <div className="border-b bg-card">
      <div className="container mx-auto px-4 py-8">
        {/* Logo and Name */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-start space-x-6">
            {organization.logo_url ? (
              <img
                src={organization.logo_url}
                alt={`${organization.name} logo`}
                className="h-24 w-24 rounded-xl object-cover"
              />
            ) : (
              <div className="h-24 w-24 rounded-xl bg-primary/10 flex items-center justify-center">
                <Building2 className="h-12 w-12 text-primary" />
              </div>
            )}

            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold">{organization.name}</h1>
                {organization.is_verified && (
                  <VerifiedBadge size="lg" />
                )}
              </div>
              <p className="text-muted-foreground mb-3">@{organization.slug}</p>

              {/* Stats */}
              <div className="flex items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-muted-foreground" />
                  <span>
                    <span className="font-semibold">
                      {formatNumber(organization.member_count)}
                    </span>{' '}
                    <span className="text-muted-foreground">
                      {organization.member_count === 1 ? 'member' : 'members'}
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          {isAdmin && onSettingsClick && (
            <Button variant="outline" onClick={onSettingsClick}>
              Settings
            </Button>
          )}
        </div>

        {/* Description */}
        {organization.description && (
          <p className="text-muted-foreground mb-4 max-w-3xl">
            {organization.description}
          </p>
        )}

        {/* Website link */}
        {organization.website_url && (
          <a
            href={organization.website_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
          >
            <ExternalLink className="h-4 w-4" />
            {new URL(organization.website_url).hostname}
          </a>
        )}
      </div>
    </div>
  );
}
