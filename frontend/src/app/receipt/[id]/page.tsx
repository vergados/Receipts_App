'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ReceiptDetail } from '@/components/receipts';
import { Spinner } from '@/components/ui';
import type { Receipt } from '@/lib/types';

export default function ReceiptPage({ params }: { params: { id: string } }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['receipt', params.id],
    queryFn: async () => {
      const res = await apiClient.get<Receipt>(`/receipts/${params.id}`);
      return res.data;
    },
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner /></div>;
  if (error || !data) return <div className="text-center py-12">Receipt not found</div>;

  return (
    <div className="container mx-auto px-4 py-6 max-w-2xl">
      <ReceiptDetail receipt={data} />
    </div>
  );
}
