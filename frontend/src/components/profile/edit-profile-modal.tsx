'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Loader2, User } from 'lucide-react';
import type { UserPublic } from '@/lib/types';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { useAuthStore } from '@/state/auth-store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Avatar } from '@/components/ui/avatar';

interface EditProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: UserPublic;
}

export function EditProfileModal({ isOpen, onClose, user }: EditProfileModalProps) {
  const queryClient = useQueryClient();
  const { setUser } = useAuthStore();
  const [displayName, setDisplayName] = useState(user.display_name);
  const [bio, setBio] = useState(user.bio || '');
  const [avatarUrl, setAvatarUrl] = useState(user.avatar_url || '');
  const [error, setError] = useState<string | null>(null);

  // Reset form when user changes
  useEffect(() => {
    setDisplayName(user.display_name);
    setBio(user.bio || '');
    setAvatarUrl(user.avatar_url || '');
  }, [user]);

  const updateMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.patch('/users/me', {
        display_name: displayName.trim() || undefined,
        bio: bio.trim() || null,
        avatar_url: avatarUrl.trim() || null,
      });
      return response.data as UserPublic;
    },
    onSuccess: (updatedUser) => {
      // Update auth store
      setUser({
        ...updatedUser,
        email: '', // These fields are in UserPrivate but not UserPublic
        is_verified: false,
        is_moderator: false,
        updated_at: null,
        last_login_at: null,
      } as any);
      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: ['user', user.handle] });
      queryClient.invalidateQueries({ queryKey: ['auth'] });
      onClose();
    },
    onError: (err) => {
      setError(getErrorMessage(err));
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!displayName.trim()) {
      setError('Display name is required');
      return;
    }

    updateMutation.mutate();
  };

  const handleClose = () => {
    setDisplayName(user.display_name);
    setBio(user.bio || '');
    setAvatarUrl(user.avatar_url || '');
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative bg-background rounded-lg shadow-lg w-full max-w-md mx-4 p-6">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-2 mb-6">
          <User className="h-5 w-5" />
          <h2 className="text-lg font-semibold">Edit Profile</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
              {error}
            </div>
          )}

          {/* Avatar Preview */}
          <div className="flex justify-center">
            <Avatar
              src={avatarUrl || undefined}
              fallback={displayName}
              size="xl"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Avatar URL</label>
            <Input
              placeholder="https://example.com/avatar.jpg"
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Enter a URL to an image for your profile picture
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">
              Display Name <span className="text-destructive">*</span>
            </label>
            <Input
              placeholder="Your name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              maxLength={100}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Bio</label>
            <Textarea
              placeholder="Tell us about yourself..."
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              className="min-h-[100px]"
              maxLength={500}
            />
            <p className="text-xs text-muted-foreground text-right">
              {bio.length}/500
            </p>
          </div>

          <div className="flex gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={handleClose}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={updateMutation.isPending}
            >
              {updateMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
