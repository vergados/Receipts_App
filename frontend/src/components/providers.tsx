'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider as NextThemesProvider } from 'next-themes';
import { Toaster } from 'sonner';
import { useState, useEffect } from 'react';
import { useAuthInit } from '@/state/auth-store';

function AuthInitializer({ children }: { children: React.ReactNode }) {
  const checkAuth = useAuthInit();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return <>{children}</>;
}

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        retry: 1,
      },
    },
  }));

  return (
    <QueryClientProvider client={client}>
      {children}
    </QueryClientProvider>
  );
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </NextThemesProvider>
  );
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <QueryProvider>
        <AuthInitializer>
          {children}
        </AuthInitializer>
        <Toaster richColors position="top-right" />
      </QueryProvider>
    </ThemeProvider>
  );
}
