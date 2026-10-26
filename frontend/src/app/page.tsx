'use client';

import Link from 'next/link';
import { ReceiptFeed } from '@/components/receipts';
import { Button, Card } from '@/components/ui';
import { useAuthStore } from '@/state/auth-store';

export default function HomePage() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="container mx-auto px-4 py-6 max-w-2xl">
      {!isAuthenticated && (
        <Card className="p-5 mb-6">
          <h2 className="text-lg font-semibold mb-1">Claims with proof.</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Every post on Receipts is a claim backed by evidence: screenshots, links, videos or quotes.
            Disagree? Answer with a counter-receipt and your own proof.
          </p>
          <div className="flex gap-2">
            <Link href="/register"><Button size="sm">Sign up free</Button></Link>
            <Link href="/login"><Button size="sm" variant="outline">Log in</Button></Link>
          </div>
        </Card>
      )}
      <h1 className="text-2xl font-bold mb-6">Latest Receipts</h1>
      <ReceiptFeed />
    </div>
  );
}
