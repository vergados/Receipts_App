'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { TrendingUp, GitFork } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Card, Spinner, Badge, Avatar } from '@/components/ui';
import { formatRelativeTime, formatNumber } from '@/lib/utils';
import type { TrendingResponse } from '@/lib/types';

export default function TrendingPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['trending'],
    queryFn: async () => {
      const res = await apiClient.get<TrendingResponse>('/feed/trending');
      return res.data;
    },
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-6 max-w-2xl">
        <h1 className="text-2xl font-bold mb-6">Trending</h1>
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container mx-auto px-4 py-6 max-w-2xl">
        <h1 className="text-2xl font-bold mb-6">Trending</h1>
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">Failed to load trending</p>
          <button onClick={() => refetch()} className="text-primary hover:underline">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const chains = data?.chains || [];

  return (
    <div className="container mx-auto px-4 py-6 max-w-2xl">
      <div className="flex items-center gap-2 mb-6">
        <TrendingUp className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-bold">Trending</h1>
      </div>

      {chains.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No trending receipts yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {chains.map((chain, index) => (
            <Link key={chain.root_receipt.id} href={`/receipt/${chain.root_receipt.id}`}>
              <Card className="p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm shrink-0">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <Avatar
                        src={chain.root_receipt.author.avatar_url}
                        fallback={chain.root_receipt.author.display_name}
                        size="sm"
                      />
                      <span className="font-medium text-sm">
                        {chain.root_receipt.author.display_name}
                      </span>
                      <span className="text-muted-foreground text-sm">
                        @{chain.root_receipt.author.handle}
                      </span>
                    </div>
                    <p className="text-sm mb-2 line-clamp-2">
                      {chain.root_receipt.claim_text}
                    </p>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span>{formatRelativeTime(chain.root_receipt.created_at)}</span>
                      {chain.fork_count > 0 && (
                        <Badge variant="secondary" className="text-xs">
                          <GitFork className="h-3 w-3 mr-1" />
                          {chain.fork_count} counter{chain.fork_count !== 1 ? 's' : ''}
                        </Badge>
                      )}
                      <span className="flex items-center gap-1">
                        <TrendingUp className="h-3 w-3" />
                        {formatNumber(chain.engagement_score)} engagement
                      </span>
                    </div>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
