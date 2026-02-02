'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { cn } from '@/lib/utils';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="flex items-center gap-1 p-1 rounded-full bg-muted">
        <div className="p-1.5 rounded-full">
          <Sun className="h-4 w-4" />
        </div>
        <div className="p-1.5 rounded-full">
          <Moon className="h-4 w-4" />
        </div>
        <div className="p-1.5 rounded-full">
          <Monitor className="h-4 w-4" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1 p-1 rounded-full bg-muted">
      <button
        onClick={() => setTheme('light')}
        className={cn(
          'p-1.5 rounded-full transition-colors',
          theme === 'light' ? 'bg-background shadow-sm' : 'hover:bg-background/50'
        )}
        title="Light mode"
      >
        <Sun className={cn('h-4 w-4', theme === 'light' ? 'text-yellow-500' : 'text-muted-foreground')} />
      </button>
      <button
        onClick={() => setTheme('dark')}
        className={cn(
          'p-1.5 rounded-full transition-colors',
          theme === 'dark' ? 'bg-background shadow-sm' : 'hover:bg-background/50'
        )}
        title="Dark mode"
      >
        <Moon className={cn('h-4 w-4', theme === 'dark' ? 'text-blue-500' : 'text-muted-foreground')} />
      </button>
      <button
        onClick={() => setTheme('system')}
        className={cn(
          'p-1.5 rounded-full transition-colors',
          theme === 'system' ? 'bg-background shadow-sm' : 'hover:bg-background/50'
        )}
        title="System preference"
      >
        <Monitor className={cn('h-4 w-4', theme === 'system' ? 'text-primary' : 'text-muted-foreground')} />
      </button>
    </div>
  );
}

// Simple dropdown version
export function ThemeDropdown() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <button className="p-2 rounded-full hover:bg-muted transition-colors">
        <Sun className="h-5 w-5" />
      </button>
    );
  }

  const cycleTheme = () => {
    if (theme === 'light') setTheme('dark');
    else if (theme === 'dark') setTheme('system');
    else setTheme('light');
  };

  return (
    <button
      onClick={cycleTheme}
      className="p-2 rounded-full hover:bg-muted transition-colors"
      title={`Current: ${theme}`}
    >
      {theme === 'light' && <Sun className="h-5 w-5 text-yellow-500" />}
      {theme === 'dark' && <Moon className="h-5 w-5 text-blue-500" />}
      {theme === 'system' && <Monitor className="h-5 w-5" />}
    </button>
  );
}
