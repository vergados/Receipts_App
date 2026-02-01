'use client';

import { useSearchParams } from 'next/navigation';
import { useInfiniteQuery } from '@tanstack/react-query';
import { useInView } from 'react-intersection-observer';
import { useEffect, Suspense } from 'react';
import { Search } from 'lucide-react';
import type { FeedResponse } from '@/lib/types';
import { apiClient } from '@/lib/api-client';
import { ReceiptCard, ReceiptCardSkeleton } from '@/components/receipts/receipt-card';
import { Button } from '@/components/ui/button';

async function searchReceipts(query: string, cursor?: string): Promise<FeedResponse> {
  const params = new URLSearchParams();
  params.set('q', query);
  params.set('limit', '20');
  if (cursor) {
    params.set('cursor', cursor);
  }
  const response = await apiClient.get(`/search?${params.toString()}`);
  return response.data;
}

function SearchResults() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';
  const { ref, inView } = useInView();

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
    refetch,
  } = useInfiniteQuery({
    queryKey: ['search', query],
    queryFn: ({ pageParam }) => searchReceipts(query, pageParam),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) =>
      lastPage.pagination.has_more ? lastPage.pagination.next_cursor : undefined,
    enabled: !!query,
  });

  // Auto-load more when scrolling
  useEffect(() => {
    if (inView && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [inView, hasNextPage, isFetchingNextPage, fetchNextPage]);

  if (!query) {
    return (
      <div className="text-center py-12">
        <Search className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
        <p className="text-muted-foreground">Enter a search term to find receipts</p>
      </div>
    );
  }

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
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground mb-4">Failed to search receipts</p>
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
        <Search className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
        <p className="text-muted-foreground">No receipts found for "{query}"</p>
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
            No more results
          </p>
        )}
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <div className="container mx-auto px-4 py-6 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">Search Results</h1>
      <Suspense fallback={
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <ReceiptCardSkeleton key={i} />
          ))}
        </div>
      }>
        <SearchResults />
      </Suspense>
    </div>
  );
}
