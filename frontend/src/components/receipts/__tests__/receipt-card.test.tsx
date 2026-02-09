import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReceiptCard, ReceiptCardSkeleton } from '../receipt-card';
import type { Receipt } from '@/lib/types';

// Mock the useReaction hook so ReceiptCard does not need a real QueryClient for reactions
vi.mock('@/lib/hooks/use-reaction', () => ({
  useReaction: () => ({
    reactions: { support: 5, dispute: 2, bookmark: 1 },
    hasReaction: () => false,
    toggleReaction: vi.fn(),
    isLoading: false,
  }),
}));

const mockReceipt: Receipt = {
  id: 'receipt-1',
  author: {
    id: 'user-1',
    handle: 'testuser',
    display_name: 'Test User',
    avatar_url: null,
  },
  claim_text: 'This is a test claim that proves something important.',
  claim_type: 'text',
  implication_text: null,
  parent_receipt_id: null,
  topic_ids: [],
  visibility: 'public',
  evidence: [
    {
      id: 'ev-1',
      type: 'image',
      content_uri: '/img.png',
      source_url: null,
      captured_at: null,
      caption: null,
      order_index: 0,
      created_at: new Date().toISOString(),
    },
  ],
  reactions: { support: 5, dispute: 2, bookmark: 1 },
  fork_count: 3,
  created_at: new Date().toISOString(),
  updated_at: null,
};

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
}

describe('ReceiptCard', () => {
  it('renders claim text', () => {
    renderWithProviders(<ReceiptCard receipt={mockReceipt} />);
    expect(screen.getByText(/This is a test claim/)).toBeInTheDocument();
  });

  it('renders author info', () => {
    renderWithProviders(<ReceiptCard receipt={mockReceipt} />);
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('@testuser')).toBeInTheDocument();
  });

  it('renders evidence type labels', () => {
    renderWithProviders(<ReceiptCard receipt={mockReceipt} />);
    // The component renders evidence type as capitalized text in a span
    expect(screen.getByText('image')).toBeInTheDocument();
  });
});

describe('ReceiptCardSkeleton', () => {
  it('renders without error', () => {
    const { container } = render(<ReceiptCardSkeleton />);
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });
});
