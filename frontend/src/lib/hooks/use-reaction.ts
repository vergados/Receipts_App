'use client';

import { useState, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { ReactionType, ReactionCounts } from '@/lib/types';
import { useAuthStore } from '@/state/auth-store';

interface UseReactionOptions {
  receiptId: string;
  initialReactions: ReactionCounts;
  onError?: (error: Error) => void;
}

interface UseReactionReturn {
  reactions: ReactionCounts;
  userReactions: Set<ReactionType>;
  toggleReaction: (type: ReactionType) => void;
  isLoading: boolean;
}

export function useReaction({
  receiptId,
  initialReactions,
  onError,
}: UseReactionOptions): UseReactionReturn {
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();

  // Track current reaction counts (for optimistic updates)
  const [reactions, setReactions] = useState<ReactionCounts>(initialReactions);

  // Track which reactions the user has made
  const [userReactions, setUserReactions] = useState<Set<ReactionType>>(new Set());

  // Add reaction mutation
  const addMutation = useMutation({
    mutationFn: async (type: ReactionType) => {
      const response = await apiClient.post(`/receipts/${receiptId}/reactions`, { type });
      return response.data;
    },
    onMutate: async (type: ReactionType) => {
      // Optimistic update
      setReactions((prev) => ({
        ...prev,
        [type]: prev[type] + 1,
      }));
      setUserReactions((prev) => new Set(prev).add(type));
    },
    onError: (error, type) => {
      // Rollback on error
      setReactions((prev) => ({
        ...prev,
        [type]: Math.max(0, prev[type] - 1),
      }));
      setUserReactions((prev) => {
        const next = new Set(prev);
        next.delete(type);
        return next;
      });
      onError?.(error as Error);
    },
    onSuccess: () => {
      // Invalidate feed queries to reflect updated counts
      queryClient.invalidateQueries({ queryKey: ['feed'] });
      queryClient.invalidateQueries({ queryKey: ['receipt', receiptId] });
    },
  });

  // Remove reaction mutation
  const removeMutation = useMutation({
    mutationFn: async (type: ReactionType) => {
      await apiClient.delete(`/receipts/${receiptId}/reactions`, {
        params: { type },
      });
    },
    onMutate: async (type: ReactionType) => {
      // Optimistic update
      setReactions((prev) => ({
        ...prev,
        [type]: Math.max(0, prev[type] - 1),
      }));
      setUserReactions((prev) => {
        const next = new Set(prev);
        next.delete(type);
        return next;
      });
    },
    onError: (error, type) => {
      // Rollback on error
      setReactions((prev) => ({
        ...prev,
        [type]: prev[type] + 1,
      }));
      setUserReactions((prev) => new Set(prev).add(type));
      onError?.(error as Error);
    },
    onSuccess: () => {
      // Invalidate feed queries to reflect updated counts
      queryClient.invalidateQueries({ queryKey: ['feed'] });
      queryClient.invalidateQueries({ queryKey: ['receipt', receiptId] });
    },
  });

  const toggleReaction = useCallback(
    (type: ReactionType) => {
      if (!isAuthenticated) {
        // Redirect to login or show message
        window.location.href = '/login';
        return;
      }

      if (userReactions.has(type)) {
        removeMutation.mutate(type);
      } else {
        addMutation.mutate(type);
      }
    },
    [isAuthenticated, userReactions, addMutation, removeMutation]
  );

  return {
    reactions,
    userReactions,
    toggleReaction,
    isLoading: addMutation.isPending || removeMutation.isPending,
  };
}
