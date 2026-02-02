'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { Bell, ThumbsUp, ThumbsDown, Bookmark, GitFork, Check, Loader2, Trash2 } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Avatar } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import { cn, formatRelativeTime } from '@/lib/utils';
import type { Notification, NotificationListResponse, NotificationType } from '@/lib/types';
import { useAuthStore } from '@/state/auth-store';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

const notificationConfig: Record<NotificationType, { icon: React.ReactNode; text: string; color: string }> = {
  receipt_support: {
    icon: <ThumbsUp className="h-5 w-5" />,
    text: 'supported your receipt',
    color: 'text-green-600',
  },
  receipt_dispute: {
    icon: <ThumbsDown className="h-5 w-5" />,
    text: 'disputed your receipt',
    color: 'text-red-600',
  },
  receipt_counter: {
    icon: <GitFork className="h-5 w-5" />,
    text: 'countered your receipt',
    color: 'text-primary',
  },
  receipt_bookmark: {
    icon: <Bookmark className="h-5 w-5" />,
    text: 'bookmarked your receipt',
    color: 'text-primary',
  },
  new_follower: {
    icon: <Bell className="h-5 w-5" />,
    text: 'started following you',
    color: 'text-primary',
  },
  mention: {
    icon: <Bell className="h-5 w-5" />,
    text: 'mentioned you',
    color: 'text-primary',
  },
};

function NotificationCard({ notification, onRead }: { notification: Notification; onRead: () => void }) {
  const config = notificationConfig[notification.type];

  const handleClick = () => {
    if (!notification.is_read) {
      onRead();
    }
  };

  const content = (
    <Card
      className={cn(
        'p-4 hover:shadow-md transition-shadow cursor-pointer',
        !notification.is_read && 'border-primary/30 bg-primary/5'
      )}
      onClick={handleClick}
    >
      <div className="flex items-start gap-4">
        {notification.actor && (
          <Avatar
            src={notification.actor.avatar_url}
            fallback={notification.actor.display_name}
            size="lg"
          />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={cn('shrink-0', config.color)}>{config.icon}</span>
            <p className="text-sm">
              {notification.actor && (
                <span className="font-medium">{notification.actor.display_name}</span>
              )}{' '}
              {config.text}
            </p>
            {!notification.is_read && (
              <div className="w-2 h-2 rounded-full bg-primary shrink-0" />
            )}
          </div>
          {notification.receipt && (
            <p className="text-sm text-muted-foreground mt-2">
              "{notification.receipt.claim_text.slice(0, 150)}
              {notification.receipt.claim_text.length > 150 ? '...' : ''}"
            </p>
          )}
          <p className="text-xs text-muted-foreground mt-2">
            {formatRelativeTime(notification.created_at)}
          </p>
        </div>
      </div>
    </Card>
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

export default function NotificationsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['notifications', 'all'],
    queryFn: async () => {
      const res = await apiClient.get<NotificationListResponse>('/notifications?limit=50');
      return res.data;
    },
    enabled: isAuthenticated,
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

  const deleteAllMutation = useMutation({
    mutationFn: async () => {
      await apiClient.delete('/notifications');
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

  const handleDeleteAll = () => {
    if (window.confirm('Are you sure you want to delete all notifications?')) {
      deleteAllMutation.mutate();
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12 max-w-2xl">
        <div className="flex justify-center">
          <Spinner />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container mx-auto px-4 py-12 max-w-2xl text-center">
        <p className="text-muted-foreground mb-4">Failed to load notifications</p>
        <Button variant="outline" onClick={() => refetch()}>Try Again</Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 max-w-2xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Bell className="h-6 w-6" />
          <h1 className="text-2xl font-bold">Notifications</h1>
          {(data?.unread_count || 0) > 0 && (
            <span className="px-2 py-0.5 rounded-full bg-primary text-primary-foreground text-sm font-medium">
              {data?.unread_count}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {(data?.unread_count || 0) > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleMarkAllRead}
              disabled={markReadMutation.isPending}
            >
              {markReadMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Check className="h-4 w-4 mr-2" />
              )}
              Mark all read
            </Button>
          )}
          {(data?.total || 0) > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleDeleteAll}
              disabled={deleteAllMutation.isPending}
              className="text-destructive hover:text-destructive"
            >
              {deleteAllMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Trash2 className="h-4 w-4 mr-2" />
              )}
              Clear all
            </Button>
          )}
        </div>
      </div>

      {data?.notifications.length === 0 ? (
        <Card className="p-12 text-center">
          <Bell className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-lg font-medium mb-2">No notifications</h2>
          <p className="text-muted-foreground">
            When someone interacts with your receipts, you'll see it here.
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {data?.notifications.map((notification) => (
            <NotificationCard
              key={notification.id}
              notification={notification}
              onRead={() => handleMarkOneRead(notification.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
