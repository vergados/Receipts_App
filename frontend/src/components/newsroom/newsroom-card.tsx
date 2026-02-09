'use client';

import Link from 'next/link';
import { Users, Building2 } from 'lucide-react';
import type { Organization } from '@/lib/types';
import { Card } from '@/components/ui/card';
import { VerifiedBadge } from './verified-badge';
import { cn, formatNumber } from '@/lib/utils';

interface NewsroomCardProps {
  organization: Organization;
  className?: string;
}

export function NewsroomCard({ organization, className }: NewsroomCardProps) {
  return (
    <Link href={`/newsroom/${organization.slug}`}>
      <Card
        className={cn(
          'p-6 hover:shadow-lg transition-all cursor-pointer group',
          className
        )}
      >
        {/* Logo and Name */}
        <div className="flex items-start space-x-4 mb-4">
          {organization.logo_url ? (
            <img
              src={organization.logo_url}
              alt={`${organization.name} logo`}
              className="h-12 w-12 rounded-lg object-cover"
            />
          ) : (
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <Building2 className="h-6 w-6 text-primary" />
            </div>
          )}

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-lg truncate group-hover:text-primary transition-colors">
                {organization.name}
              </h3>
              {organization.is_verified && (
                <VerifiedBadge size="md" />
              )}
            </div>
            <p className="text-sm text-muted-foreground">@{organization.slug}</p>
          </div>
        </div>

        {/* Description */}
        {organization.description && (
          <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
            {organization.description}
          </p>
        )}

        {/* Stats */}
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <Users className="h-4 w-4" />
            <span>
              {formatNumber(organization.member_count)}{' '}
              {organization.member_count === 1 ? 'member' : 'members'}
            </span>
          </div>
        </div>
      </Card>
    </Link>
  );
}
