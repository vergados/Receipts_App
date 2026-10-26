'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { ReceiptDetail } from '@/components/receipts';
import { Spinner } from '@/components/ui';
import type { Receipt, ReceiptChain } from '@/lib/types';

export default function ReceiptPage({ params }: { params: { id: string } }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['receipt', params.id],
    queryFn: async () => {
      const res = await apiClient.get<Receipt>(`/receipts/${params.id}`);
      return res.data;
    },
  });

  // Counter-receipts made against this receipt
  const { data: chain } = useQuery({
    queryKey: ['receipt-chain', params.id],
    queryFn: async () => {
      const res = await apiClient.get<ReceiptChain>(`/receipts/${params.id}/chain`);
      return res.data;
    },
    enabled: !!data && data.fork_count > 0,
  });

  // The receipt this one is countering, if any
  const parentId = data?.parent_receipt_id;
  const { data: parent } = useQuery({
    queryKey: ['receipt', parentId],
    queryFn: async () => {
      const res = await apiClient.get<Receipt>(`/receipts/${parentId}`);
      return res.data;
    },
    enabled: !!parentId,
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner /></div>;
  if (error || !data) return <div className="text-center py-12">Receipt not found</div>;

  return (
    <div className="container mx-auto px-4 py-6 max-w-2xl">
      <ReceiptDetail receipt={data} chain={chain} parent={parent} />
    </div>
  );
}
