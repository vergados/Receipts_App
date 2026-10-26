'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  ThumbsUp, ThumbsDown, Bookmark, GitFork, Share2, Flag,
  Image, Link as LinkIcon, Video, Quote, ExternalLink,
  ChevronDown, ChevronUp, Check
} from 'lucide-react';
import type { Receipt, ReceiptChain, ReceiptChainNode, EvidenceItem, EvidenceType } from '@/lib/types';
import { formatRelativeTime, formatDateTime, formatNumber, cn } from '@/lib/utils';
import { useReaction } from '@/lib/hooks/use-reaction';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { VideoPlayer } from '@/components/ui/video-player';
import { ReportModal } from '@/components/moderation/report-modal';

interface ReceiptDetailProps {
  receipt: Receipt;
  chain?: ReceiptChain;
  parent?: Receipt;
}

const evidenceIcons: Record<EvidenceType, React.ReactNode> = {
  image: <Image className="h-4 w-4" />,
  link: <LinkIcon className="h-4 w-4" />,
  video: <Video className="h-4 w-4" />,
  quote: <Quote className="h-4 w-4" />,
};

function EvidenceCard({ evidence }: { evidence: EvidenceItem }) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <Card className="overflow-hidden">
      <div className="p-3 bg-muted/50 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {evidenceIcons[evidence.type]}
          <span className="text-sm font-medium capitalize">{evidence.type}</span>
        </div>
        {evidence.captured_at && (
          <span className="text-xs text-muted-foreground">
            Captured {formatRelativeTime(evidence.captured_at)}
          </span>
        )}
      </div>
      
      <div className="p-4">
        {evidence.type === 'image' && (
          <div className="relative aspect-video bg-muted rounded-md overflow-hidden">
            <img
              src={evidence.content_uri}
              alt={evidence.caption || 'Evidence'}
              className="object-contain w-full h-full"
            />
          </div>
        )}
        
        {evidence.type === 'link' && (
          <a
            href={evidence.content_uri}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 text-primary hover:underline"
          >
            <ExternalLink className="h-4 w-4" />
            <span className="truncate">{evidence.content_uri}</span>
          </a>
        )}
        
        {evidence.type === 'quote' && (
          <blockquote className="border-l-4 border-primary/30 pl-4 italic text-muted-foreground">
            &ldquo;{evidence.content_uri.replace(/^["“”']+|["“”']+$/g, '')}&rdquo;
          </blockquote>
        )}
        
        {evidence.type === 'video' && (
          <VideoPlayer src={evidence.content_uri} />
        )}
        
        {evidence.caption && (
          <p className="mt-3 text-sm text-muted-foreground">
            {evidence.caption}
          </p>
        )}
        
        {evidence.source_url && (
          <a
            href={evidence.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 flex items-center space-x-1 text-xs text-primary hover:underline"
          >
            <span>Source</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        )}
      </div>
    </Card>
  );
}

function CounterReceiptList({ nodes, depth = 0 }: { nodes: ReceiptChainNode[]; depth?: number }) {
  return (
    <div className={cn('space-y-3', depth > 0 && 'mt-3 pl-4 border-l-2 border-muted')}>
      {nodes.map((node) => (
        <div key={node.id}>
          <Link href={`/receipt/${node.id}`} className="block">
            <Card className="p-4 hover:border-primary/50 transition-colors">
              <div className="flex items-center space-x-2 mb-2">
                <Avatar src={node.author.avatar_url} fallback={node.author.display_name} size="sm" />
                <span className="text-sm font-medium">{node.author.display_name}</span>
                <span className="text-xs text-muted-foreground">@{node.author.handle}</span>
                <span className="text-xs text-muted-foreground">· {formatRelativeTime(node.created_at)}</span>
              </div>
              <p className="text-sm mb-2">{node.claim_text}</p>
              <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                <span className="flex items-center"><ThumbsUp className="h-3 w-3 mr-1" />{formatNumber(node.reactions.support)} support</span>
                <span className="flex items-center"><ThumbsDown className="h-3 w-3 mr-1" />{formatNumber(node.reactions.dispute)} dispute</span>
              </div>
            </Card>
          </Link>
          {node.forks.length > 0 && <CounterReceiptList nodes={node.forks} depth={depth + 1} />}
        </div>
      ))}
    </div>
  );
}

export function ReceiptDetail({ receipt, chain, parent }: ReceiptDetailProps) {
  const [showAllEvidence, setShowAllEvidence] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [copied, setCopied] = useState(false);

  const { reactions, hasReaction, toggleReaction } = useReaction({
    receiptId: receipt.id,
    initialReactions: receipt.reactions,
  });

  const visibleEvidence = showAllEvidence
    ? receipt.evidence
    : receipt.evidence.slice(0, 3);

  const handleShare = async () => {
    const url = `${window.location.origin}/receipt/${receipt.id}`;

    // Try native share API first (works on mobile with HTTPS)
    if (typeof navigator !== 'undefined' && navigator.share) {
      try {
        await navigator.share({
          title: 'Receipt',
          text: receipt.claim_text.slice(0, 100) + (receipt.claim_text.length > 100 ? '...' : ''),
          url,
        });
        return;
      } catch (err: any) {
        // Only fall through if it's not a user abort
        if (err?.name === 'AbortError') return;
      }
    }

    // Try clipboard API
    if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
      try {
        await navigator.clipboard.writeText(url);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        return;
      } catch (err) {
        // Clipboard failed, try fallback
      }
    }

    // Fallback: create temporary input and copy
    try {
      const input = document.createElement('input');
      input.value = url;
      input.style.position = 'fixed';
      input.style.opacity = '0';
      document.body.appendChild(input);
      input.focus();
      input.select();
      const success = document.execCommand('copy');
      document.body.removeChild(input);
      if (success) {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        return;
      }
    } catch (err) {
      // Fallback failed
    }

    // Last resort: show prompt with URL
    window.prompt('Copy this link:', url);
  };
  
  return (
    <div className="space-y-6">
      {/* Main Receipt Card */}
      <Card className="p-6">
        {/* Author Header */}
        <div className="flex items-start justify-between mb-4">
          <Link 
            href={`/u/${receipt.author.handle}`}
            className="flex items-center space-x-3 hover:opacity-80"
          >
            <Avatar
              src={receipt.author.avatar_url}
              fallback={receipt.author.display_name}
              size="lg"
            />
            <div>
              <div className="font-semibold">{receipt.author.display_name}</div>
              <div className="text-sm text-muted-foreground">
                @{receipt.author.handle}
              </div>
            </div>
          </Link>
          
          <div className="flex items-center space-x-2">
            {receipt.parent_receipt_id && (
              <Badge>
                <GitFork className="h-3 w-3 mr-1" />
                Counter-receipt
              </Badge>
            )}
          </div>
        </div>
        
        {/* Parent Receipt Reference */}
        {receipt.parent_receipt_id && parent && (
          <div className="mb-4 p-3 bg-muted/50 rounded-lg">
            <p className="text-xs text-muted-foreground mb-1">Responding to:</p>
            <Link 
              href={`/receipt/${receipt.parent_receipt_id}`}
              className="text-sm text-primary hover:underline"
            >
              {parent.claim_text.length > 100 ? `${parent.claim_text.slice(0, 100)}…` : parent.claim_text}
            </Link>
          </div>
        )}
        
        {/* Claim */}
        <div className="mb-6">
          <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
            Claim
          </h2>
          <p className="text-lg leading-relaxed">{receipt.claim_text}</p>
        </div>
        
        {/* Implication */}
        {receipt.implication_text && (
          <div className="mb-6 pl-4 border-l-4 border-primary/30">
            <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
              Implication
            </h2>
            <p className="text-muted-foreground italic">
              {receipt.implication_text}
            </p>
          </div>
        )}
        
        {/* Evidence */}
        <div className="mb-6">
          <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-3">
            Evidence ({receipt.evidence.length})
          </h2>
          <div className="space-y-4">
            {visibleEvidence.map((evidence) => (
              <EvidenceCard key={evidence.id} evidence={evidence} />
            ))}
          </div>
          
          {receipt.evidence.length > 3 && (
            <Button
              variant="ghost"
              size="sm"
              className="mt-3 w-full"
              onClick={() => setShowAllEvidence(!showAllEvidence)}
            >
              {showAllEvidence ? (
                <>
                  <ChevronUp className="h-4 w-4 mr-2" />
                  Show less
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4 mr-2" />
                  Show all {receipt.evidence.length} evidence items
                </>
              )}
            </Button>
          )}
        </div>
        
        {/* Timestamp */}
        <div className="text-sm text-muted-foreground mb-6">
          {formatDateTime(receipt.created_at)}
        </div>
        
        {/* Actions */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-4 border-t">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => toggleReaction('support')}
              aria-label="Support"
              title="Support: the evidence backs this up"
              className={cn(
                hasReaction('support') && "bg-green-600 hover:bg-green-700 text-white border-green-600"
              )}
            >
              <ThumbsUp className={cn("h-4 w-4 mr-2", hasReaction('support') && "fill-current")} />
              <span className="hidden sm:inline mr-1">Support</span>
              {formatNumber(reactions.support)}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => toggleReaction('dispute')}
              aria-label="Dispute"
              title="Dispute: the evidence doesn't hold up"
              className={cn(
                hasReaction('dispute') && "bg-red-600 hover:bg-red-700 text-white border-red-600"
              )}
            >
              <ThumbsDown className={cn("h-4 w-4 mr-2", hasReaction('dispute') && "fill-current")} />
              <span className="hidden sm:inline mr-1">Dispute</span>
              {formatNumber(reactions.dispute)}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => toggleReaction('bookmark')}
              aria-label="Save"
              title="Save for later"
              className={cn(
                hasReaction('bookmark') && "bg-primary hover:bg-primary/90 text-primary-foreground border-primary"
              )}
            >
              <Bookmark className={cn("h-4 w-4 mr-2", hasReaction('bookmark') && "fill-current")} />
              {formatNumber(reactions.bookmark)}
            </Button>
          </div>

          <div className="flex items-center gap-1">
            <Link href={`/create?fork=${receipt.id}`}>
              <Button variant="secondary" size="sm" title="Disagree? Post your own receipt with proof">
                <GitFork className="h-4 w-4 mr-2" />
                Counter with proof
              </Button>
            </Link>
            <Button variant="ghost" size="sm" onClick={handleShare} className="relative" aria-label="Copy link" title="Copy link">
              {copied ? (
                <>
                  <Check className="h-4 w-4 text-green-600" />
                  <span className="ml-1 text-xs text-green-600">Copied!</span>
                </>
              ) : (
                <Share2 className="h-4 w-4" />
              )}
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setShowReportModal(true)} aria-label="Report" title="Report">
              <Flag className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>

      {/* Report Modal */}
      <ReportModal
        isOpen={showReportModal}
        onClose={() => setShowReportModal(false)}
        targetType="receipt"
        targetId={receipt.id}
      />
      
      {/* Counter-receipts */}
      {receipt.fork_count > 0 && (
        <div>
          <h2 className="flex items-center text-sm font-medium mb-3">
            <GitFork className="h-4 w-4 mr-2" />
            {receipt.fork_count} counter-receipt{receipt.fork_count !== 1 ? 's' : ''}
          </h2>
          {chain ? (
            <CounterReceiptList nodes={chain.forks} />
          ) : (
            <p className="text-sm text-muted-foreground">Loading…</p>
          )}
        </div>
      )}
    </div>
  );
}
