'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { X, Flag, Loader2 } from 'lucide-react';
import type { ReportReason, TargetType } from '@/lib/types';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

interface ReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  targetType: TargetType;
  targetId: string;
}

const reportReasons: { value: ReportReason; label: string; description: string }[] = [
  { value: 'misinformation', label: 'Misinformation', description: 'False or misleading information' },
  { value: 'harassment', label: 'Harassment', description: 'Targeting or bullying an individual' },
  { value: 'doxxing', label: 'Doxxing', description: 'Sharing private information' },
  { value: 'spam', label: 'Spam', description: 'Irrelevant or repetitive content' },
  { value: 'other', label: 'Other', description: 'Another reason not listed' },
];

export function ReportModal({ isOpen, onClose, targetType, targetId }: ReportModalProps) {
  const [selectedReason, setSelectedReason] = useState<ReportReason | null>(null);
  const [details, setDetails] = useState('');
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reportMutation = useMutation({
    mutationFn: async () => {
      if (!selectedReason) throw new Error('Please select a reason');
      const response = await apiClient.post('/reports', {
        target_type: targetType,
        target_id: targetId,
        reason: selectedReason,
        details: details.trim() || null,
      });
      return response.data;
    },
    onSuccess: () => {
      setSuccess(true);
      setError(null);
    },
    onError: (err) => {
      setError(getErrorMessage(err));
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReason) {
      setError('Please select a reason');
      return;
    }
    reportMutation.mutate();
  };

  const handleClose = () => {
    setSelectedReason(null);
    setDetails('');
    setSuccess(false);
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative bg-background rounded-lg shadow-lg w-full max-w-md mx-4 p-6">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-2 mb-4">
          <Flag className="h-5 w-5 text-destructive" />
          <h2 className="text-lg font-semibold">Report Content</h2>
        </div>

        {success ? (
          <div className="text-center py-6">
            <div className="text-green-600 mb-2">Report submitted</div>
            <p className="text-sm text-muted-foreground mb-4">
              Thank you for helping keep our community safe. We'll review your report.
            </p>
            <Button onClick={handleClose}>Close</Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label className="text-sm font-medium">Why are you reporting this?</label>
              <div className="space-y-2">
                {reportReasons.map((reason) => (
                  <button
                    key={reason.value}
                    type="button"
                    onClick={() => setSelectedReason(reason.value)}
                    className={cn(
                      "w-full p-3 rounded-md border text-left transition-colors",
                      selectedReason === reason.value
                        ? "border-primary bg-primary/5"
                        : "border-input hover:bg-muted/50"
                    )}
                  >
                    <div className="font-medium text-sm">{reason.label}</div>
                    <div className="text-xs text-muted-foreground">{reason.description}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Additional details <span className="text-muted-foreground">(optional)</span>
              </label>
              <Textarea
                placeholder="Provide any additional context..."
                value={details}
                onChange={(e) => setDetails(e.target.value)}
                className="min-h-[80px]"
                maxLength={500}
              />
            </div>

            <div className="flex gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                className="flex-1"
                onClick={handleClose}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="destructive"
                className="flex-1"
                disabled={!selectedReason || reportMutation.isPending}
              >
                {reportMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  'Submit Report'
                )}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
