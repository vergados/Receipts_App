'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Receipt, Search, Plus, User, LogOut, Menu, X, Shield, Building2 } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Avatar } from '@/components/ui/avatar';
import { ThemeDropdown } from '@/components/ui/theme-toggle';
import { NotificationDropdown } from '@/components/notifications/notification-dropdown';
import { useAuthStore } from '@/state/auth-store';
import { cn } from '@/lib/utils';

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
      setMobileMenuOpen(false);
    }
  };

  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/trending', label: 'Trending' },
    { href: '/topics', label: 'Topics' },
    { href: '/newsroom', label: 'Newsrooms' },
  ];
  
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 overflow-visible">
      <div className="container mx-auto flex h-16 items-center px-4">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2 mr-6">
          <Receipt className="h-6 w-6 text-primary" />
          <span className="font-bold text-xl">Receipts</span>
        </Link>
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-6 flex-1">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                'text-sm font-medium transition-colors hover:text-primary',
                pathname === link.href ? 'text-primary' : 'text-muted-foreground'
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>
        
        {/* Search - Desktop */}
        <form onSubmit={handleSearch} className="hidden md:flex items-center mx-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="search"
              placeholder="Search receipts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-9 w-64 rounded-md border border-input bg-background pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </form>
        
        {/* Actions */}
        <div className="flex items-center space-x-2">
          <ThemeDropdown />

          {isAuthenticated ? (
            <>
              <Link href="/create">
                <Button size="sm" className="hidden sm:flex">
                  <Plus className="h-4 w-4 mr-2" />
                  New Receipt
                </Button>
                <Button size="icon" variant="ghost" className="sm:hidden">
                  <Plus className="h-5 w-5" />
                </Button>
              </Link>

              <NotificationDropdown />

              <div className="relative">
                <button
                  className="flex items-center space-x-2"
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                >
                  <Avatar
                    src={user?.avatar_url}
                    fallback={user?.display_name}
                    size="sm"
                  />
                </button>

                {/* Dropdown */}
                {userMenuOpen && (
                  <div className="absolute right-0 top-full mt-2 w-48 rounded-md border bg-background shadow-lg z-50">
                    <div className="p-2">
                      <div className="px-2 py-1.5 text-sm font-medium">
                        {user?.display_name}
                      </div>
                      <div className="px-2 py-1 text-xs text-muted-foreground">
                        @{user?.handle}
                      </div>
                    </div>
                    <div className="border-t">
                      <Link
                        href={`/u/${user?.handle}`}
                        className="flex items-center px-2 py-2 text-sm hover:bg-accent"
                        onClick={() => setUserMenuOpen(false)}
                      >
                        <User className="h-4 w-4 mr-2" />
                        Profile
                      </Link>
                      {user?.organization_id && (
                        <Link
                          href="/newsroom/dashboard"
                          className="flex items-center px-2 py-2 text-sm hover:bg-accent"
                          onClick={() => setUserMenuOpen(false)}
                        >
                          <Building2 className="h-4 w-4 mr-2" />
                          Newsroom
                        </Link>
                      )}
                      {user?.is_moderator && (
                        <Link
                          href="/admin"
                          className="flex items-center px-2 py-2 text-sm hover:bg-accent"
                          onClick={() => setUserMenuOpen(false)}
                        >
                          <Shield className="h-4 w-4 mr-2" />
                          Admin
                        </Link>
                      )}
                      <button
                        onClick={() => { logout(); setUserMenuOpen(false); }}
                        className="flex w-full items-center px-2 py-2 text-sm hover:bg-accent text-destructive"
                      >
                        <LogOut className="h-4 w-4 mr-2" />
                        Logout
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Login
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm">Sign Up</Button>
              </Link>
            </>
          )}
          
          {/* Mobile menu button */}
          <button
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t">
          <nav className="container mx-auto px-4 py-4 space-y-4">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'block text-sm font-medium transition-colors hover:text-primary',
                  pathname === link.href ? 'text-primary' : 'text-muted-foreground'
                )}
                onClick={() => setMobileMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <form onSubmit={handleSearch} className="pt-4 border-t">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="search"
                  placeholder="Search receipts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="h-10 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
            </form>
          </nav>
        </div>
      )}
    </header>
  );
}
