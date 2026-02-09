'use client';

import { useState, FormEvent } from 'react';
import { Mail, Send, AlertCircle, Check } from 'lucide-react';
import type { OrganizationRole, Department } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useOrganizationStore } from '@/state/organization-store';

interface InviteFormProps {
  organizationId: string;
  departments?: Department[];
  onSuccess?: () => void;
}

const roleOptions: { value: OrganizationRole; label: string; description: string }[] = [
  {
    value: 'reporter',
    label: 'Reporter',
    description: 'Can create receipts, needs approval to publish',
  },
  {
    value: 'senior_reporter',
    label: 'Senior Reporter',
    description: 'Can create and publish receipts directly',
  },
  {
    value: 'editor',
    label: 'Editor',
    description: 'Can review, publish, and manage team content',
  },
  {
    value: 'admin',
    label: 'Admin',
    description: 'Full access to organization settings and team',
  },
  {
    value: 'contributor',
    label: 'Contributor',
    description: 'Limited access, can create draft content',
  },
];

export function InviteForm({
  organizationId,
  departments = [],
  onSuccess,
}: InviteFormProps) {
  const { sendInvitation, isLoading, error, clearError } = useOrganizationStore();

  const [email, setEmail] = useState('');
  const [role, setRole] = useState<OrganizationRole>('reporter');
  const [departmentId, setDepartmentId] = useState<string>('');
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    setShowSuccess(false);

    if (!email || !email.includes('@')) {
      return;
    }

    try {
      await sendInvitation(organizationId, {
        email,
        role,
        department_id: departmentId || null,
      });

      // Success!
      setShowSuccess(true);
      setEmail('');
      setDepartmentId('');
      onSuccess?.();

      // Hide success message after 3 seconds
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (err) {
      // Error is handled by store
    }
  };

  return (
    <Card className="p-6">
      <div className="flex items-center gap-2 mb-4">
        <Mail className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold">Invite Team Member</h3>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email Input */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-2">
            Email Address
          </label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="colleague@example.com"
            required
            disabled={isLoading}
          />
        </div>

        {/* Role Selection */}
        <div>
          <label htmlFor="role" className="block text-sm font-medium mb-2">
            Role
          </label>
          <select
            id="role"
            value={role}
            onChange={(e) => setRole(e.target.value as OrganizationRole)}
            className="w-full px-3 py-2 border rounded-md bg-background"
            disabled={isLoading}
          >
            {roleOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-muted-foreground mt-1">
            {roleOptions.find((r) => r.value === role)?.description}
          </p>
        </div>

        {/* Department Selection (Optional) */}
        {departments.length > 0 && (
          <div>
            <label htmlFor="department" className="block text-sm font-medium mb-2">
              Department (Optional)
            </label>
            <select
              id="department"
              value={departmentId}
              onChange={(e) => setDepartmentId(e.target.value)}
              className="w-full px-3 py-2 border rounded-md bg-background"
              disabled={isLoading}
            >
              <option value="">No department</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>
                  {dept.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="flex items-start gap-2 p-3 bg-destructive/10 text-destructive rounded-md text-sm">
            <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Success Message */}
        {showSuccess && (
          <div className="flex items-start gap-2 p-3 bg-green-500/10 text-green-600 dark:text-green-400 rounded-md text-sm">
            <Check className="h-4 w-4 mt-0.5 shrink-0" />
            <span>Invitation sent successfully to {email}!</span>
          </div>
        )}

        {/* Submit Button */}
        <Button type="submit" disabled={isLoading || !email} className="w-full">
          {isLoading ? (
            <>Sending...</>
          ) : (
            <>
              <Send className="h-4 w-4 mr-2" />
              Send Invitation
            </>
          )}
        </Button>
      </form>
    </Card>
  );
}
