'use client';

import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { Bell, ThumbsUp, ThumbsDown, Bookmark, GitFork, Check, Loader2 } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Avatar } from '@/components/ui/avatar';
import { useAuthStore } from '@/state/auth-store';
import { cn, formatRelativeTime } from '@/lib/utils';
import type { Notification, NotificationListResponse, NotificationType } from '@/lib/types';

const notificationConfig: Record<NotificationType, { icon: React.ReactNode; text: string; color: string }> = {
  receipt_support: {
    icon: <ThumbsUp className="h-4 w-4" />,
    text: 'supported your receipt',
    color: 'text-green-600',
  },
  receipt_dispute: {
    icon: <ThumbsDown className="h-4 w-4" />,
    text: 'disputed your receipt',
    color: 'text-red-600',
  },
  receipt_counter: {
    icon: <GitFork className="h-4 w-4" />,
    text: 'countered your receipt',
    color: 'text-primary',
  },
  receipt_bookmark: {
    icon: <Bookmark className="h-4 w-4" />,
    text: 'bookmarked your receipt',
    color: 'text-primary',
  },
  new_follower: {
    icon: <Bell className="h-4 w-4" />,
    text: 'started following you',
    color: 'text-primary',
  },
  mention: {
    icon: <Bell className="h-4 w-4" />,
    text: 'mentioned you',
    color: 'text-primary',
  },
};

function NotificationItem({ notification, onRead }: { notification: Notification; onRead: () => void }) {
  const config = notificationConfig[notification.type];

  const handleClick = () => {
    if (!notification.is_read) {
      onRead();
    }
  };

  const content = (
    <div
      className={cn(
        'flex items-start gap-3 p-3 hover:bg-muted/50 transition-colors cursor-pointer',
        !notification.is_read && 'bg-primary/5'
      )}
      onClick={handleClick}
    >
      {notification.actor && (
        <Avatar
          src={notification.actor.avatar_url}
          fallback={notification.actor.display_name}
          size="sm"
        />
      )}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <span className={cn('shrink-0', config.color)}>{config.icon}</span>
          <p className="text-sm">
            {notification.actor && (
              <span className="font-medium">{notification.actor.display_name}</span>
            )}{' '}
            {config.text}
          </p>
        </div>
        {notification.receipt && (
          <p className="text-xs text-muted-foreground truncate mt-1">
            "{notification.receipt.claim_text.slice(0, 60)}
            {notification.receipt.claim_text.length > 60 ? '...' : ''}"
          </p>
        )}
        <p className="text-xs text-muted-foreground mt-1">
          {formatRelativeTime(notification.created_at)}
        </p>
      </div>
      {!notification.is_read && (
        <div className="w-2 h-2 rounded-full bg-primary shrink-0 mt-2" />
      )}
    </div>
  );

  if (notification.receipt) {
    return (
      <Link href={`/receipt/${notification.receipt.id}`}>
        {content}
      </Link>
    );
  }

  if (notification.actor) {
    return (
      <Link href={`/u/${notification.actor.handle}`}>
        {content}
      </Link>
    );
  }

  return content;
}

export function NotificationDropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const res = await apiClient.get<NotificationListResponse>('/notifications?limit=10');
      return res.data;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
    enabled: isAuthenticated, // Only fetch when authenticated
    retry: 1,
  });

  const markReadMutation = useMutation({
    mutationFn: async (notificationIds?: string[]) => {
      await apiClient.post('/notifications/mark-read', {
        notification_ids: notificationIds || null,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const handleMarkAllRead = () => {
    markReadMutation.mutate(undefined);
  };

  const handleMarkOneRead = (id: string) => {
    markReadMutation.mutate([id]);
  };

  const unreadCount = data?.unread_count || 0;

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Mobile: Link to notifications page */}
      <Link
        href="/notifications"
        className="relative p-2 rounded-full hover:bg-muted transition-colors sm:hidden block"
        aria-label="Notifications"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-white">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </Link>

      {/* Desktop: Dropdown */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-full hover:bg-muted transition-colors hidden sm:block"
        aria-label="Notifications"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-white">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 rounded-md border bg-background shadow-lg z-50 hidden sm:block">
          <div className="flex items-center justify-between p-3 border-b">
            <h3 className="font-semibold">Notifications</h3>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                disabled={markReadMutation.isPending}
                className="text-xs text-primary hover:underline disabled:opacity-50 flex items-center gap-1"
              >
                {markReadMutation.isPending ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <Check className="h-3 w-3" />
                )}
                Mark all read
              </button>
            )}
          </div>

          <div className="max-h-96 overflow-y-auto">
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : isError ? (
              <div className="text-center py-8 text-sm text-muted-foreground">
                Failed to load notifications
              </div>
            ) : data?.notifications.length === 0 ? (
              <div className="text-center py-8 text-sm text-muted-foreground">
                No notifications yet
              </div>
            ) : (
              <div className="divide-y">
                {data?.notifications.map((notification) => (
                  <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onRead={() => handleMarkOneRead(notification.id)}
                  />
                ))}
              </div>
            )}
          </div>

          {(data?.total || 0) > 10 && (
            <div className="p-2 border-t text-center">
              <Link
                href="/notifications"
                className="text-sm text-primary hover:underline"
                onClick={() => setIsOpen(false)}
              >
                View all notifications
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
