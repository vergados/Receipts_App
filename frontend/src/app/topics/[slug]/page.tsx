'use client';

import { useParams } from 'next/navigation';
import { Hash } from 'lucide-react';
import { ReceiptFeed } from '@/components/receipts/receipt-feed';

export default function TopicPage() {
  const params = useParams();
  const slug = params.slug as string;

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6 flex items-center gap-3">
          <div className="p-3 rounded-lg bg-primary/10">
            <Hash className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold capitalize">{slug.replace(/-/g, ' ')}</h1>
            <p className="text-muted-foreground">Receipts in this topic</p>
          </div>
        </div>

        <ReceiptFeed
          endpoint={`/feed/topic/${slug}`}
          queryKey={['feed', 'topic', slug]}
        />
      </div>
    </div>
  );
}
