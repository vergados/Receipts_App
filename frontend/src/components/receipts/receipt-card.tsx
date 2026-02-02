'use client';

import Link from 'next/link';
import { ThumbsUp, ThumbsDown, Bookmark, GitFork, Image, Link as LinkIcon, Video, Quote } from 'lucide-react';
import type { Receipt, EvidenceType } from '@/lib/types';
import { formatRelativeTime, truncate, formatNumber } from '@/lib/utils';
import { useReaction } from '@/lib/hooks/use-reaction';
import { Card } from '@/components/ui/card';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface ReceiptCardProps {
  receipt: Receipt;
  showFullClaim?: boolean;
}

const evidenceIcons: Record<EvidenceType, React.ReactNode> = {
  image: <Image className="h-3 w-3" />,
  link: <LinkIcon className="h-3 w-3" />,
  video: <Video className="h-3 w-3" />,
  quote: <Quote className="h-3 w-3" />,
};

export function ReceiptCard({ receipt, showFullClaim = false }: ReceiptCardProps) {
  const claimText = showFullClaim
    ? receipt.claim_text
    : truncate(receipt.claim_text, 280);

  const { reactions, hasReaction, toggleReaction } = useReaction({
    receiptId: receipt.id,
    initialReactions: receipt.reactions,
  });

  const handleReaction = (e: React.MouseEvent, type: 'support' | 'dispute' | 'bookmark') => {
    e.preventDefault();
    e.stopPropagation();
    toggleReaction(type);
  };

  return (
    <Link href={`/receipt/${receipt.id}`}>
      <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer">
        {/* Header: Author info */}
        <div className="flex items-center space-x-3 mb-3">
          <Avatar
            src={receipt.author.avatar_url}
            fallback={receipt.author.display_name}
            size="sm"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <span className="font-medium text-sm truncate">
                {receipt.author.display_name}
              </span>
              <span className="text-muted-foreground text-sm">
                @{receipt.author.handle}
              </span>
            </div>
            <span className="text-xs text-muted-foreground">
              {formatRelativeTime(receipt.created_at)}
            </span>
          </div>

          {receipt.parent_receipt_id && (
            <Badge variant="secondary" className="shrink-0">
              <GitFork className="h-3 w-3 mr-1" />
              Counter
            </Badge>
          )}
        </div>

        {/* Claim */}
        <div className="mb-3">
          <p className="text-sm leading-relaxed">{claimText}</p>
        </div>

        {/* Implication (if present) */}
        {receipt.implication_text && (
          <div className="mb-3 pl-3 border-l-2 border-primary/30">
            <p className="text-sm text-muted-foreground italic">
              {truncate(receipt.implication_text, 150)}
            </p>
          </div>
        )}

        {/* Evidence Preview */}
        <div className="flex flex-wrap gap-2 mb-3">
          {receipt.evidence.slice(0, 4).map((item) => (
            <div
              key={item.id}
              className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-muted text-xs"
            >
              {evidenceIcons[item.type]}
              <span className="capitalize">{item.type}</span>
            </div>
          ))}
          {receipt.evidence.length > 4 && (
            <div className="inline-flex items-center px-2 py-1 rounded-md bg-muted text-xs">
              +{receipt.evidence.length - 4} more
            </div>
          )}
        </div>

        {/* Footer: Reactions */}
        <div className="flex items-center justify-between pt-3 border-t">
          <div className="flex items-center space-x-4">
            <button
              onClick={(e) => handleReaction(e, 'support')}
              className={cn(
                "flex items-center space-x-1 transition-colors",
                hasReaction('support')
                  ? "text-green-600"
                  : "text-muted-foreground hover:text-green-600"
              )}
            >
              <ThumbsUp className={cn("h-4 w-4", hasReaction('support') && "fill-current")} />
              <span className="text-xs">{formatNumber(reactions.support)}</span>
            </button>
            <button
              onClick={(e) => handleReaction(e, 'dispute')}
              className={cn(
                "flex items-center space-x-1 transition-colors",
                hasReaction('dispute')
                  ? "text-red-600"
                  : "text-muted-foreground hover:text-red-600"
              )}
            >
              <ThumbsDown className={cn("h-4 w-4", hasReaction('dispute') && "fill-current")} />
              <span className="text-xs">{formatNumber(reactions.dispute)}</span>
            </button>
            <Link
              href={`/create?fork=${receipt.id}`}
              onClick={(e) => e.stopPropagation()}
              className="flex items-center space-x-1 text-muted-foreground hover:text-primary transition-colors"
            >
              <GitFork className="h-4 w-4" />
              <span className="text-xs">{formatNumber(receipt.fork_count)}</span>
            </Link>
          </div>
          <button
            onClick={(e) => handleReaction(e, 'bookmark')}
            className={cn(
              "transition-colors",
              hasReaction('bookmark')
                ? "text-primary"
                : "text-muted-foreground hover:text-primary"
            )}
          >
            <Bookmark className={cn("h-4 w-4", hasReaction('bookmark') && "fill-current")} />
          </button>
        </div>
      </Card>
    </Link>
  );
}

// Skeleton for loading state
export function ReceiptCardSkeleton() {
  return (
    <Card className="p-4">
      <div className="flex items-center space-x-3 mb-3">
        <div className="h-8 w-8 rounded-full bg-muted animate-pulse" />
        <div className="flex-1 space-y-2">
          <div className="h-4 w-32 bg-muted rounded animate-pulse" />
          <div className="h-3 w-20 bg-muted rounded animate-pulse" />
        </div>
      </div>
      <div className="space-y-2 mb-3">
        <div className="h-4 w-full bg-muted rounded animate-pulse" />
        <div className="h-4 w-3/4 bg-muted rounded animate-pulse" />
      </div>
      <div className="flex gap-2 mb-3">
        <div className="h-6 w-16 bg-muted rounded animate-pulse" />
        <div className="h-6 w-16 bg-muted rounded animate-pulse" />
      </div>
      <div className="flex items-center justify-between pt-3 border-t">
        <div className="flex space-x-4">
          <div className="h-4 w-12 bg-muted rounded animate-pulse" />
          <div className="h-4 w-12 bg-muted rounded animate-pulse" />
          <div className="h-4 w-12 bg-muted rounded animate-pulse" />
        </div>
      </div>
    </Card>
  );
}
