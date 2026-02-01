'use client';

import * as React from 'react';
import Image from 'next/image';
import { cn, getInitials } from '@/lib/utils';

export interface AvatarProps {
  src?: string | null;
  alt?: string;
  fallback?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export function Avatar({ src, alt = '', fallback, size = 'md', className }: AvatarProps) {
  const [hasError, setHasError] = React.useState(false);
  
  const sizes = {
    sm: 'h-8 w-8 text-xs',
    md: 'h-10 w-10 text-sm',
    lg: 'h-12 w-12 text-base',
    xl: 'h-16 w-16 text-lg',
  };
  
  const pixelSizes = {
    sm: 32,
    md: 40,
    lg: 48,
    xl: 64,
  };
  
  const initials = fallback ? getInitials(fallback) : alt ? getInitials(alt) : '?';
  
  if (!src || hasError) {
    return (
      <div
        className={cn(
          'inline-flex items-center justify-center rounded-full bg-primary/10 text-primary font-medium',
          sizes[size],
          className
        )}
      >
        {initials}
      </div>
    );
  }
  
  return (
    <div className={cn('relative rounded-full overflow-hidden bg-muted', sizes[size], className)}>
      <Image
        src={src}
        alt={alt}
        width={pixelSizes[size]}
        height={pixelSizes[size]}
        className="object-cover"
        onError={() => setHasError(true)}
      />
    </div>
  );
}
