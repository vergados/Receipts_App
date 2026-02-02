'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Pencil } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { ReceiptFeed } from '@/components/receipts';
import { Avatar, Card, Spinner, Button } from '@/components/ui';
import { EditProfileModal } from '@/components/profile/edit-profile-modal';
import { useAuthStore } from '@/state/auth-store';
import type { UserPublic } from '@/lib/types';
import { formatDate } from '@/lib/utils';

export default function ProfilePage({ params }: { params: { handle: string } }) {
  const [showEditModal, setShowEditModal] = useState(false);
  const { user: currentUser } = useAuthStore();

  const { data: user, isLoading } = useQuery({
    queryKey: ['user', params.handle],
    queryFn: async () => {
      const res = await apiClient.get<UserPublic>(`/users/${params.handle}`);
      return res.data;
    },
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner /></div>;
  if (!user) return <div className="text-center py-12">User not found</div>;

  const isOwnProfile = currentUser?.handle === user.handle;

  return (
    <div className="container mx-auto px-4 py-6 max-w-2xl">
      <Card className="p-6 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <Avatar src={user.avatar_url} fallback={user.display_name} size="xl" />
            <div>
              <h1 className="text-xl font-bold">{user.display_name}</h1>
              <p className="text-muted-foreground">@{user.handle}</p>
              {user.bio && <p className="mt-2">{user.bio}</p>}
              <p className="text-sm text-muted-foreground mt-2">
                {user.receipt_count} receipts · Joined {formatDate(user.created_at)}
              </p>
            </div>
          </div>
          {isOwnProfile && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowEditModal(true)}
            >
              <Pencil className="h-4 w-4 mr-2" />
              Edit
            </Button>
          )}
        </div>
      </Card>
      <ReceiptFeed endpoint={`/users/${params.handle}/receipts`} queryKey={['user-receipts', params.handle]} />

      {isOwnProfile && (
        <EditProfileModal
          isOpen={showEditModal}
          onClose={() => setShowEditModal(false)}
          user={user}
        />
      )}
    </div>
  );
}
