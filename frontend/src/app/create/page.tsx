'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Plus, X, Image, Link as LinkIcon, Video, Quote } from 'lucide-react';
import { Button, Input, Textarea, Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import type { EvidenceCreate, EvidenceType } from '@/lib/types';

const evidenceIcons = { image: Image, link: LinkIcon, video: Video, quote: Quote };

export default function CreatePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const forkId = searchParams.get('fork');
  
  const [claim, setClaim] = useState('');
  const [implication, setImplication] = useState('');
  const [evidence, setEvidence] = useState<EvidenceCreate[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const addEvidence = (type: EvidenceType) => {
    setEvidence([...evidence, { type, content_uri: '', caption: '' }]);
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
                  <Input
                    placeholder={ev.type === 'quote' ? 'Quote text' : 'URL'}
                    value={ev.content_uri}
                    onChange={(e) => updateEvidence(idx, 'content_uri', e.target.value)}
                    className="mb-2"
                  />
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
