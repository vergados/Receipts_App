import { ReceiptFeed } from '@/components/receipts';

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-6 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">Latest Receipts</h1>
      <ReceiptFeed />
    </div>
  );
}
