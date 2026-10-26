'use client';

import { Suspense, useState, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { X, Image, Link as LinkIcon, Video, Quote, Upload, Loader2, Building2, GitFork } from 'lucide-react';
import { Button, Input, Textarea, Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { RequireAuth } from '@/components/auth';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { toast } from 'sonner';
import { useAuthStore } from '@/state/auth-store';
import { cn } from '@/lib/utils';
import type { EvidenceCreate, EvidenceType, Receipt, TopicListResponse } from '@/lib/types';

const evidenceOptions: { type: EvidenceType; label: string; icon: typeof Image }[] = [
  { type: 'image', label: 'Screenshot / photo', icon: Image },
  { type: 'link', label: 'Link', icon: LinkIcon },
  { type: 'video', label: 'Video', icon: Video },
  { type: 'quote', label: 'Quote', icon: Quote },
];

const evidenceLabels: Record<EvidenceType, string> = {
  image: 'Screenshot / photo',
  link: 'Link',
  video: 'Video',
  quote: 'Quote',
};

const MAX_TOPICS = 5;
const CLAIM_MAX = 1000;

export default function CreatePage() {
  return (
    <RequireAuth>
      <Suspense>
        <CreatePageContent />
      </Suspense>
    </RequireAuth>
  );
}

function CreatePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const forkId = searchParams.get('fork');
  const { user } = useAuthStore();

  const [claim, setClaim] = useState('');
  const [implication, setImplication] = useState('');
  const [evidence, setEvidence] = useState<EvidenceCreate[]>([]);
  const [topicIds, setTopicIds] = useState<string[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState<number | null>(null);
  const fileInputRefs = useRef<Record<number, HTMLInputElement | null>>({});

  // Newsroom fields
  const [isBreakingNews, setIsBreakingNews] = useState(false);
  const isNewsroomMember = !!user?.organization_id;

  // The receipt being countered, so the user can see what they're answering
  const { data: parent } = useQuery({
    queryKey: ['receipt', forkId],
    queryFn: async () => (await apiClient.get<Receipt>(`/receipts/${forkId}`)).data,
    enabled: !!forkId,
  });

  const { data: topicData } = useQuery({
    queryKey: ['topics'],
    queryFn: async () => (await apiClient.get<TopicListResponse>('/topics')).data,
  });

  const addEvidence = (type: EvidenceType) => {
    setEvidence([...evidence, { type, content_uri: '', caption: '' }]);
    setError('');
  };

  const toggleTopic = (id: string) => {
    setTopicIds((ids) =>
      ids.includes(id) ? ids.filter((t) => t !== id) : ids.length < MAX_TOPICS ? [...ids, id] : ids
    );
  };

  const handleFileUpload = async (idx: number, file: File) => {
    setUploading(idx);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await apiClient.post('/uploads/file', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      updateEvidence(idx, 'content_uri', res.data.content_uri);
      toast.success(file.type.startsWith('video/') ? 'Video uploaded' : 'Image uploaded');
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setUploading(null);
    }
  };

  const updateEvidence = (idx: number, field: keyof EvidenceCreate, value: string) => {
    setEvidence((current) => {
      const updated = [...current];
      updated[idx] = { ...updated[idx], [field]: value };
      return updated;
    });
  };

  const removeEvidence = (idx: number) => {
    setEvidence(evidence.filter((_, i) => i !== idx));
  };

  const isUrl = (value: string) => /^https?:\/\/\S+$/i.test(value.trim());

  // Plain-English check before sending, so customers never see a server error code
  const validate = (): string | null => {
    if (!claim.trim()) return 'Write your claim first.';
    if (evidence.length === 0) return 'Add at least one piece of evidence (a screenshot, link, video or quote).';
    for (let i = 0; i < evidence.length; i++) {
      const ev = evidence[i];
      const name = `${evidenceLabels[ev.type]} #${i + 1}`;
      if (!ev.content_uri.trim()) {
        if (ev.type === 'image' || ev.type === 'video') return `${name} is empty. Choose a file or paste a link, or remove it.`;
        if (ev.type === 'quote') return `${name} is empty. Type the quote, or remove it.`;
        return `${name} is empty. Paste the web address, or remove it.`;
      }
      if (ev.type === 'link' && !isUrl(ev.content_uri)) return `${name} needs a full web address starting with https://`;
      if (ev.source_url && !isUrl(ev.source_url)) return `The source for ${name} needs a full web address starting with https://`;
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const problem = validate();
    if (problem) {
      setError(problem);
      return;
    }
    setError('');
    setLoading(true);

    try {
      const endpoint = forkId ? `/receipts/${forkId}/fork` : '/receipts';
      const payload: any = {
        claim_text: claim,
        implication_text: implication || undefined,
        ...(forkId ? {} : { topic_ids: topicIds }),
        evidence: evidence.map((ev) => ({
          ...ev,
          caption: ev.caption || undefined,
          source_url: ev.source_url || undefined,
        })),
      };

      // Add newsroom fields if user is a newsroom member
      if (isNewsroomMember && user?.organization_id) {
        payload.organization_id = user.organization_id;
        payload.is_breaking_news = isBreakingNews;
      }

      const res = await apiClient.post(endpoint, payload);
      toast.success(forkId ? 'Counter-receipt posted' : 'Receipt posted');
      router.push(`/receipt/${res.data.id}`);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-6 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>{forkId ? 'Counter with proof' : 'New Receipt'}</CardTitle>
          <p className="text-sm text-muted-foreground">
            {forkId
              ? 'Disagree? Make your own claim and back it up with evidence.'
              : 'A receipt is a claim backed by proof. Say what happened, then show the evidence.'}
          </p>
        </CardHeader>
        <CardContent>
          {forkId && parent && (
            <div className="mb-4 p-3 bg-muted/50 rounded-lg">
              <p className="flex items-center text-xs text-muted-foreground mb-1">
                <GitFork className="h-3 w-3 mr-1" />
                Countering @{parent.author.handle}:
              </p>
              <p className="text-sm">{parent.claim_text}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5" noValidate>
            <div>
              <label htmlFor="claim" className="text-sm font-medium block mb-1">Claim</label>
              <p className="text-xs text-muted-foreground mb-2">What happened? Be specific: who, what, when.</p>
              <Textarea
                id="claim"
                placeholder="e.g. The city council voted 5-2 to approve bike lanes on Main St. on Oct 12."
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                maxLength={CLAIM_MAX}
                className="min-h-[100px]"
              />
              <p className="text-xs text-muted-foreground text-right mt-1">{claim.length}/{CLAIM_MAX}</p>
            </div>

            <div>
              <p className="text-sm font-medium mb-1">Evidence <span className="text-muted-foreground font-normal">(at least one)</span></p>
              <p className="text-xs text-muted-foreground mb-2">Add proof that backs up your claim.</p>
              <div className="flex flex-wrap gap-2 mb-3">
                {evidenceOptions.map(({ type, label, icon: Icon }) => (
                  <Button key={type} type="button" variant="outline" size="sm" onClick={() => addEvidence(type)}>
                    <Icon className="h-4 w-4 mr-1" /> {label}
                  </Button>
                ))}
              </div>

              {evidence.map((ev, idx) => (
                <div key={idx} className="border rounded p-3 mb-2 relative">
                  <button
                    type="button"
                    onClick={() => removeEvidence(idx)}
                    className="absolute top-2 right-2"
                    aria-label={`Remove ${evidenceLabels[ev.type]}`}
                  >
                    <X className="h-4 w-4" />
                  </button>
                  <p className="text-xs font-medium mb-2">{evidenceLabels[ev.type]}</p>

                  {(ev.type === 'image' || ev.type === 'video') ? (
                    <div className="space-y-2 mb-2">
                      {ev.content_uri && ev.type === 'image' && (
                        <div className="rounded overflow-hidden border bg-muted">
                          <img
                            src={ev.content_uri}
                            alt="Preview"
                            className="max-h-48 mx-auto object-contain"
                          />
                        </div>
                      )}
                      <div className="flex gap-2">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={uploading === idx}
                          onClick={() => fileInputRefs.current[idx]?.click()}
                        >
                          {uploading === idx ? (
                            <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                          ) : (
                            <Upload className="h-4 w-4 mr-1" />
                          )}
                          {uploading === idx ? 'Uploading...' : 'Choose file'}
                        </Button>
                        <span className="text-xs text-muted-foreground self-center">or paste a link below</span>
                      </div>
                      <input
                        type="file"
                        accept={ev.type === 'image'
                          ? 'image/png,image/jpeg,image/gif,image/webp'
                          : 'video/mp4,video/webm,video/quicktime,video/x-msvideo,video/x-matroska,video/mpeg,.mov,.mp4'}
                        className="hidden"
                        ref={(el) => { fileInputRefs.current[idx] = el; }}
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) handleFileUpload(idx, file);
                          e.target.value = '';
                        }}
                      />
                      <Input
                        placeholder="https://..."
                        value={ev.content_uri}
                        onChange={(e) => updateEvidence(idx, 'content_uri', e.target.value)}
                      />
                    </div>
                  ) : ev.type === 'quote' ? (
                    <div className="space-y-2 mb-2">
                      <Textarea
                        placeholder="Exact words, e.g. Motion carries five to two."
                        value={ev.content_uri}
                        onChange={(e) => updateEvidence(idx, 'content_uri', e.target.value)}
                        maxLength={500}
                      />
                      <Input
                        placeholder="Where is this from? Link to the source (optional)"
                        value={ev.source_url || ''}
                        onChange={(e) => updateEvidence(idx, 'source_url', e.target.value)}
                      />
                    </div>
                  ) : (
                    <Input
                      placeholder="https://..."
                      value={ev.content_uri}
                      onChange={(e) => updateEvidence(idx, 'content_uri', e.target.value)}
                      className="mb-2"
                    />
                  )}

                  <Input
                    placeholder="Caption: what does this show? (optional)"
                    value={ev.caption || ''}
                    onChange={(e) => updateEvidence(idx, 'caption', e.target.value)}
                  />
                </div>
              ))}
            </div>

            <div>
              <label htmlFor="implication" className="text-sm font-medium block mb-1">
                Why it matters <span className="text-muted-foreground font-normal">(optional)</span>
              </label>
              <Textarea
                id="implication"
                placeholder="e.g. Construction starts next spring and Main St. loses 40 parking spots."
                value={implication}
                onChange={(e) => setImplication(e.target.value)}
                maxLength={1000}
              />
            </div>

            {!forkId && topicData && topicData.topics.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-1">
                  Topics <span className="text-muted-foreground font-normal">(optional, up to {MAX_TOPICS})</span>
                </p>
                <div className="flex flex-wrap gap-2">
                  {topicData.topics.map((topic) => {
                    const selected = topicIds.includes(topic.id);
                    return (
                      <button
                        key={topic.id}
                        type="button"
                        onClick={() => toggleTopic(topic.id)}
                        aria-pressed={selected}
                        className={cn(
                          'px-3 py-1 rounded-full border text-sm transition-colors',
                          selected
                            ? 'bg-primary text-primary-foreground border-primary'
                            : 'text-muted-foreground hover:border-primary'
                        )}
                      >
                        {topic.name}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {isNewsroomMember && (
              <div className="border rounded-lg p-4 bg-muted/50">
                <div className="flex items-center gap-2 mb-3">
                  <Building2 className="h-4 w-4 text-primary" />
                  <p className="text-sm font-medium">{user?.organization_name}</p>
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isBreakingNews}
                    onChange={(e) => setIsBreakingNews(e.target.checked)}
                    className="w-4 h-4 rounded border-gray-300"
                  />
                  <span className="text-sm">Mark as Breaking News</span>
                </label>
              </div>
            )}

            {error && <p role="alert" className="text-sm text-destructive">{error}</p>}

            <Button type="submit" className="w-full" isLoading={loading}>
              {forkId ? 'Post counter-receipt' : 'Post Receipt'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
