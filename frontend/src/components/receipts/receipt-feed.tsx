'use client';

import { useInfiniteQuery } from '@tanstack/react-query';
import { useInView } from 'react-intersection-observer';
import { useEffect } from 'react';
import type { FeedResponse } from '@/lib/types';
import { apiClient } from '@/lib/api-client';
import { cursorToSkip } from '@/lib/utils';
import { ReceiptCard, ReceiptCardSkeleton } from './receipt-card';
import { Button } from '@/components/ui/button';

interface ReceiptFeedProps {
  endpoint?: string;
  queryKey?: string[];
}

async function fetchFeed(endpoint: string, cursor?: string): Promise<FeedResponse> {
  const params = new URLSearchParams();
  params.set('limit', '20');
  if (cursor) {
    params.set('cursor', cursor);
  }
  try {
    const response = await apiClient.get(`${endpoint}?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Feed fetch error:', error);
    throw error;
  }
}

export function ReceiptFeed({ 
  endpoint = '/feed', 
  queryKey = ['feed'] 
}: ReceiptFeedProps) {
  const { ref, inView } = useInView();
  
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
    error,
    refetch,
  } = useInfiniteQuery({
    queryKey,
    queryFn: ({ pageParam }) => fetchFeed(endpoint, pageParam),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) =>
      lastPage.pagination.has_more ? lastPage.pagination.next_cursor : undefined,
    staleTime: 0,
    refetchOnMount: 'always',
  });
  
  // Auto-load more when scrolling
  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [inView, hasNextPage, isFetchingNextPage, fetchNextPage]);
  
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <ReceiptCardSkeleton key={i} />
        ))}
      </div>
    );
  }
  
  if (isError) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Feed error:', error);
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground mb-2">
          Failed to load receipts
        </p>
        <p className="text-xs text-muted-foreground mb-4">
          {errorMessage}
        </p>
        <Button variant="outline" onClick={() => refetch()}>
          Try Again
        </Button>
      </div>
    );
  }
  
  const receipts = data?.pages.flatMap((page) => page.receipts) || [];
  
  if (receipts.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No receipts yet</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {receipts.map((receipt) => (
        <ReceiptCard key={receipt.id} receipt={receipt} />
      ))}
      
      {/* Load more trigger */}
      <div ref={ref} className="py-4">
        {isFetchingNextPage && (
          <div className="flex justify-center">
            <ReceiptCardSkeleton />
          </div>
        )}
        {!hasNextPage && receipts.length > 0 && (
          <p className="text-center text-sm text-muted-foreground">
            You've reached the end
          </p>
        )}
      </div>
    </div>
  );
}
