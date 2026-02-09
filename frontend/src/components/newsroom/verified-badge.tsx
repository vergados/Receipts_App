'use client';

import { CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface VerifiedBadgeProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  showText?: boolean;
  organizationName?: string;
}

export function VerifiedBadge({
  size = 'sm',
  className,
  showText = false,
  organizationName,
}: VerifiedBadgeProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  if (showText && organizationName) {
    return (
      <span
        className={cn(
          'inline-flex items-center gap-1 text-blue-600 dark:text-blue-400',
          textSizeClasses[size],
          className
        )}
        title={`Verified member of ${organizationName}`}
      >
        <CheckCircle2 className={cn(sizeClasses[size], 'fill-current')} />
        <span className="font-medium">{organizationName}</span>
      </span>
    );
  }

  return (
    <CheckCircle2
      className={cn(
        sizeClasses[size],
        'text-blue-600 dark:text-blue-400 fill-current',
        className
      )}
      title={organizationName ? `Verified member of ${organizationName}` : 'Verified'}
      aria-label="Verified"
    />
  );
}
