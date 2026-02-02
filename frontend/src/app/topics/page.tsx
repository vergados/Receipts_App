'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Card, Spinner } from '@/components/ui';
import type { TopicListResponse } from '@/lib/types';

export default function TopicsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['topics'],
    queryFn: async () => {
      const res = await apiClient.get<TopicListResponse>('/topics');
      return res.data;
    },
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner /></div>;

  return (
    <div className="container mx-auto px-4 py-6 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">Topics</h1>
      <div className="grid gap-4">
        {data?.topics.map((topic) => (
          <Link key={topic.id} href={`/topics/${topic.slug}`}>
            <Card className="p-4 hover:shadow-md transition-shadow">
              <h2 className="font-semibold">{topic.name}</h2>
              {topic.description && <p className="text-sm text-muted-foreground">{topic.description}</p>}
              <p className="text-xs text-muted-foreground mt-2">{topic.receipt_count} receipts</p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
