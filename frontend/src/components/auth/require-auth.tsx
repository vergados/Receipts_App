'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/state/auth-store';
import { Spinner } from '@/components/ui/spinner';

interface RequireAuthProps {
  children: React.ReactNode;
  requireModerator?: boolean;
}

export function RequireAuth({ children, requireModerator = false }: RequireAuthProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoading, user } = useAuthStore();

  useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated) {
      router.push(`/login?returnUrl=${encodeURIComponent(pathname)}`);
      return;
    }

    if (requireModerator && user && !user.is_moderator) {
      router.push('/');
    }
  }, [isAuthenticated, isLoading, user, requireModerator, router, pathname]);

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  if (requireModerator && user && !user.is_moderator) {
    return null;
  }

  return <>{children}</>;
}
