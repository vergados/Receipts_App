'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Plus, X, Image, Link as LinkIcon, Video, Quote, Loader2, Tag, Zap, Building2, FileText } from 'lucide-react';
import type { ReceiptCreate, EvidenceCreate, EvidenceType, Topic } from '@/lib/types';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAuthStore } from '@/state/auth-store';
import { useCurrentOrganization, useOrganizationStore } from '@/state/organization-store';
import { cn } from '@/lib/utils';

const evidenceTypes: { type: EvidenceType; icon: React.ReactNode; label: string }[] = [
  { type: 'image', icon: <Image className="h-4 w-4" />, label: 'Image' },
  { type: 'link', icon: <LinkIcon className="h-4 w-4" />, label: 'Link' },
  { type: 'video', icon: <Video className="h-4 w-4" />, label: 'Video' },
  { type: 'quote', icon: <Quote className="h-4 w-4" />, label: 'Quote' },
];

interface EvidenceFormItem extends EvidenceCreate {
  id: string;
}

export function CreateReceiptForm({ forkId }: { forkId?: string }) {
  const router = useRouter();
  const { user } = useAuthStore();
  const currentOrg = useCurrentOrganization();
  const { currentOrgInvestigations, loadCurrentOrgInvestigations } = useOrganizationStore();

  const [claimText, setClaimText] = useState('');
  const [implicationText, setImplicationText] = useState('');
  const [selectedTopicIds, setSelectedTopicIds] = useState<string[]>([]);
  const [evidence, setEvidence] = useState<EvidenceFormItem[]>([
    { id: '1', type: 'image', content_uri: '', caption: '' },
  ]);
  const [error, setError] = useState<string | null>(null);

  // Newsroom-specific fields
  const [publishAsOrganization, setPublishAsOrganization] = useState(false);
  const [isBreakingNews, setIsBreakingNews] = useState(false);
  const [selectedInvestigationId, setSelectedInvestigationId] = useState<string>('');

  // Load investigations if user is in a newsroom
  useEffect(() => {
    if (currentOrg) {
      loadCurrentOrgInvestigations();
    }
  }, [currentOrg?.id]);

  const isNewsroomMember = !!currentOrg;
  const isVerifiedNewsroom = currentOrg?.is_verified || false;

  // Fetch available topics
  const { data: topicsData } = useQuery({
    queryKey: ['topics'],
    queryFn: async () => {
      const response = await apiClient.get('/topics');
      return response.data as { topics: Topic[] };
    },
  });

  const topics = topicsData?.topics || [];

  const toggleTopic = (topicId: string) => {
    setSelectedTopicIds((prev) =>
      prev.includes(topicId)
        ? prev.filter((id) => id !== topicId)
        : [...prev, topicId]
    );
  };

  const createMutation = useMutation({
    mutationFn: async (data: ReceiptCreate) => {
      const endpoint = forkId ? `/receipts/${forkId}/fork` : '/receipts';
      const response = await apiClient.post(endpoint, data);
      return response.data;
    },
    onSuccess: (data) => {
      router.push(`/receipt/${data.id}`);
    },
    onError: (err) => {
      setError(getErrorMessage(err));
    },
  });

  const addEvidence = () => {
    if (evidence.length >= 10) return;
    setEvidence([
      ...evidence,
      { id: Date.now().toString(), type: 'image', content_uri: '', caption: '' },
    ]);
  };

  const removeEvidence = (id: string) => {
    if (evidence.length <= 1) return;
    setEvidence(evidence.filter((e) => e.id !== id));
  };

  const updateEvidence = (id: string, updates: Partial<EvidenceFormItem>) => {
    setEvidence(
      evidence.map((e) => (e.id === id ? { ...e, ...updates } : e))
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!claimText.trim()) {
      setError('Claim is required');
      return;
    }

    const validEvidence = evidence.filter((e) => e.content_uri.trim());
    if (validEvidence.length === 0) {
      setError('At least one piece of evidence is required');
      return;
    }

    const data: ReceiptCreate = {
      claim_text: claimText.trim(),
      implication_text: implicationText.trim() || undefined,
      topic_ids: selectedTopicIds.length > 0 ? selectedTopicIds : undefined,
      evidence: validEvidence.map(({ id, ...rest }) => rest),
      organization_id: publishAsOrganization && currentOrg ? currentOrg.id : undefined,
      is_breaking_news: isBreakingNews && isVerifiedNewsroom ? isBreakingNews : undefined,
      investigation_thread_id: selectedInvestigationId || undefined,
    };

    createMutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
          {error}
        </div>
      )}

      <div className="space-y-2">
        <label className="text-sm font-medium">
          Claim <span className="text-destructive">*</span>
        </label>
        <Textarea
          placeholder="What claim are you documenting? Be specific and factual."
          value={claimText}
          onChange={(e) => setClaimText(e.target.value)}
          className="min-h-[100px]"
          maxLength={2000}
        />
        <p className="text-xs text-muted-foreground text-right">
          {claimText.length}/2000
        </p>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">
          Why does this matter? <span className="text-muted-foreground">(optional)</span>
        </label>
        <Textarea
          placeholder="Explain the significance or implications of this claim."
          value={implicationText}
          onChange={(e) => setImplicationText(e.target.value)}
          className="min-h-[80px]"
          maxLength={1000}
        />
      </div>

      {/* Topic Selection */}
      <div className="space-y-2">
        <label className="text-sm font-medium flex items-center gap-2">
          <Tag className="h-4 w-4" />
          Topics <span className="text-muted-foreground">(optional)</span>
        </label>
        <p className="text-xs text-muted-foreground">
          Select one or more topics to help others find your receipt
        </p>
        <div className="flex flex-wrap gap-2">
          {topics.map((topic) => (
            <button
              key={topic.id}
              type="button"
              onClick={() => toggleTopic(topic.id)}
              className={cn(
                "px-3 py-1.5 rounded-full text-sm transition-colors",
                selectedTopicIds.includes(topic.id)
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted hover:bg-muted/80"
              )}
            >
              {topic.name}
            </button>
          ))}
        </div>
      </div>

      {/* Newsroom Options */}
      {isNewsroomMember && (
        <Card className="p-4 space-y-4 bg-muted/50">
          <div className="flex items-center gap-2 mb-2">
            <Building2 className="h-5 w-5 text-primary" />
            <h3 className="font-medium">Newsroom Options</h3>
          </div>

          {/* Publish as Organization */}
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={publishAsOrganization}
              onChange={(e) => setPublishAsOrganization(e.target.checked)}
              className="h-4 w-4"
            />
            <div>
              <p className="text-sm font-medium">Publish as {currentOrg?.name}</p>
              <p className="text-xs text-muted-foreground">
                This receipt will be attributed to your organization
              </p>
            </div>
          </label>

          {/* Breaking News Toggle (only for verified orgs) */}
          {isVerifiedNewsroom && publishAsOrganization && (
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={isBreakingNews}
                onChange={(e) => setIsBreakingNews(e.target.checked)}
                className="h-4 w-4"
              />
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-destructive" />
                <div>
                  <p className="text-sm font-medium">Mark as Breaking News</p>
                  <p className="text-xs text-muted-foreground">
                    Give this receipt priority visibility
                  </p>
                </div>
              </div>
            </label>
          )}

          {/* Investigation Thread Selector */}
          {publishAsOrganization && currentOrgInvestigations.length > 0 && (
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Add to Investigation
                <span className="text-muted-foreground">(optional)</span>
              </label>
              <select
                value={selectedInvestigationId}
                onChange={(e) => setSelectedInvestigationId(e.target.value)}
                className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
              >
                <option value="">None - Standalone receipt</option>
                {currentOrgInvestigations
                  .filter((inv) => !inv.is_published)
                  .map((investigation) => (
                    <option key={investigation.id} value={investigation.id}>
                      {investigation.title}
                    </option>
                  ))}
              </select>
              <p className="text-xs text-muted-foreground">
                Link this receipt to an ongoing investigation
              </p>
            </div>
          )}
        </Card>
      )}

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium">
            Evidence <span className="text-destructive">*</span>
          </label>
          <span className="text-xs text-muted-foreground">
            {evidence.length}/10 items
          </span>
        </div>

        {evidence.map((item, index) => (
          <Card key={item.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <span className="text-sm font-medium">Evidence #{index + 1}</span>
              {evidence.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeEvidence(item.id)}
                  className="text-muted-foreground hover:text-destructive"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>

            <div className="flex gap-2 mb-3">
              {evidenceTypes.map(({ type, icon, label }) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => updateEvidence(item.id, { type })}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-sm transition-colors ${
                    item.type === type
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted hover:bg-muted/80'
                  }`}
                >
                  {icon}
                  {label}
                </button>
              ))}
            </div>

            <div className="space-y-2 mb-3">
              <Input
                placeholder={
                  item.type === 'quote'
                    ? 'Enter the quoted text'
                    : item.type === 'link'
                    ? 'https://example.com/article'
                    : 'URL to image or video'
                }
                value={item.content_uri}
                onChange={(e) =>
                  updateEvidence(item.id, { content_uri: e.target.value })
                }
              />
            </div>

            {(item.type === 'quote' || item.type === 'image') && (
              <div className="space-y-2 mb-3">
                <Input
                  placeholder="Source URL (optional)"
                  value={item.source_url || ''}
                  onChange={(e) =>
                    updateEvidence(item.id, { source_url: e.target.value })
                  }
                />
              </div>
            )}

            <div className="space-y-2">
              <Input
                placeholder="Caption or description (optional)"
                value={item.caption || ''}
                onChange={(e) =>
                  updateEvidence(item.id, { caption: e.target.value })
                }
              />
            </div>
          </Card>
        ))}

        {evidence.length < 10 && (
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={addEvidence}
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Evidence
          </Button>
        )}
      </div>

      <div className="flex gap-3 pt-4">
        <Button
          type="button"
          variant="outline"
          className="flex-1"
          onClick={() => router.back()}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          className="flex-1"
          disabled={createMutation.isPending}
        >
          {createMutation.isPending ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Creating...
            </>
          ) : forkId ? (
            'Post Counter-Receipt'
          ) : (
            'Post Receipt'
          )}
        </Button>
      </div>
    </form>
  );
}
