'use client';

import { Suspense, useState, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { X, Image, Link as LinkIcon, Video, Quote, Upload, Loader2 } from 'lucide-react';
import { Button, Input, Textarea, Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { RequireAuth } from '@/components/auth';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { toast } from 'sonner';
import type { EvidenceCreate, EvidenceType } from '@/lib/types';

const evidenceIcons = { image: Image, link: LinkIcon, video: Video, quote: Quote };

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
  
  const [claim, setClaim] = useState('');
  const [implication, setImplication] = useState('');
  const [evidence, setEvidence] = useState<EvidenceCreate[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState<number | null>(null);
  const fileInputRefs = useRef<Record<number, HTMLInputElement | null>>({});

  const addEvidence = (type: EvidenceType) => {
    setEvidence([...evidence, { type, content_uri: '', caption: '' }]);
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
      toast.success('Image uploaded');
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setUploading(null);
    }
  };

  const updateEvidence = (idx: number, field: keyof EvidenceCreate, value: string) => {
    const updated = [...evidence];
    updated[idx] = { ...updated[idx], [field]: value };
    setEvidence(updated);
  };

  const removeEvidence = (idx: number) => {
    setEvidence(evidence.filter((_, i) => i !== idx));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (evidence.length === 0) {
      setError('At least one piece of evidence is required');
      return;
    }
    setError('');
    setLoading(true);

    try {
      const endpoint = forkId ? `/receipts/${forkId}/fork` : '/receipts';
      const res = await apiClient.post(endpoint, {
        claim_text: claim,
        implication_text: implication || undefined,
        evidence: evidence.filter(e => e.content_uri),
      });
      toast.success('Receipt posted successfully');
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
          <CardTitle>{forkId ? 'Create Counter-Receipt' : 'New Receipt'}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && <p className="text-sm text-destructive">{error}</p>}
            
            <Textarea
              placeholder="What's the claim? Be specific..."
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              required
              className="min-h-[100px]"
            />
            
            <Textarea
              placeholder="Why does this matter? (optional)"
              value={implication}
              onChange={(e) => setImplication(e.target.value)}
            />

            <div>
              <p className="text-sm font-medium mb-2">Evidence ({evidence.length})</p>
              <div className="flex gap-2 mb-4">
                {(Object.keys(evidenceIcons) as EvidenceType[]).map((type) => {
                  const Icon = evidenceIcons[type];
                  return (
                    <Button key={type} type="button" variant="outline" size="sm" onClick={() => addEvidence(type)}>
                      <Icon className="h-4 w-4 mr-1" /> {type}
                    </Button>
                  );
                })}
              </div>
              
              {evidence.map((ev, idx) => (
                <div key={idx} className="border rounded p-3 mb-2 relative">
                  <button type="button" onClick={() => removeEvidence(idx)} className="absolute top-2 right-2">
                    <X className="h-4 w-4" />
                  </button>
                  <p className="text-xs font-medium capitalize mb-2">{ev.type}</p>

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
                        <span className="text-xs text-muted-foreground self-center">or paste a URL below</span>
                      </div>
                      <input
                        type="file"
                        accept={ev.type === 'image' ? 'image/png,image/jpeg,image/gif,image/webp' : 'video/mp4,video/webm'}
                        className="hidden"
                        ref={(el) => { fileInputRefs.current[idx] = el; }}
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) handleFileUpload(idx, file);
                          e.target.value = '';
                        }}
                      />
                      <Input
                        placeholder="Or enter URL"
                        value={ev.content_uri}
                        onChange={(e) => updateEvidence(idx, 'content_uri', e.target.value)}
                      />
                    </div>
                  ) : (
                    <Input
                      placeholder={ev.type === 'quote' ? 'Quote text' : 'URL'}
                      value={ev.content_uri}
                      onChange={(e) => updateEvidence(idx, 'content_uri', e.target.value)}
                      className="mb-2"
                    />
                  )}

                  <Input
                    placeholder="Caption (optional)"
                    value={ev.caption || ''}
                    onChange={(e) => updateEvidence(idx, 'caption', e.target.value)}
                  />
                </div>
              ))}
            </div>

            <Button type="submit" className="w-full" isLoading={loading}>
              Post Receipt
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
