'use client';

import { useState, FormEvent } from 'react';
import { Plus, Folder, Users, Edit2, Trash2 } from 'lucide-react';
import type { Department } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatNumber } from '@/lib/utils';

interface DeskManagerProps {
  departments: Department[];
  onCreateDepartment: (data: { name: string; description?: string }) => Promise<void>;
  onDeleteDepartment?: (deptId: string) => Promise<void>;
  isLoading?: boolean;
}

export function DeskManager({
  departments,
  onCreateDepartment,
  onDeleteDepartment,
  isLoading = false,
}: DeskManagerProps) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSubmitting(true);
    try {
      await onCreateDepartment({
        name: name.trim(),
        description: description.trim() || undefined,
      });

      // Reset form
      setName('');
      setDescription('');
      setShowForm(false);
    } catch (err) {
      // Error handled by parent
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (deptId: string, deptName: string) => {
    if (!onDeleteDepartment) return;

    if (confirm(`Delete "${deptName}" department? Members will not be removed.`)) {
      try {
        await onDeleteDepartment(deptId);
      } catch (err) {
        // Error handled by parent
      }
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Folder className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold">Departments</h3>
          <Badge variant="secondary">{departments.length}</Badge>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowForm(!showForm)}
          disabled={isLoading}
        >
          <Plus className="h-4 w-4 mr-2" />
          New Department
        </Button>
      </div>

      {/* Create Form */}
      {showForm && (
        <Card className="p-4">
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label htmlFor="dept-name" className="block text-sm font-medium mb-2">
                Department Name
              </label>
              <Input
                id="dept-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Politics, Investigations, Local News"
                required
                disabled={submitting}
                autoFocus
              />
            </div>

            <div>
              <label htmlFor="dept-desc" className="block text-sm font-medium mb-2">
                Description (Optional)
              </label>
              <Textarea
                id="dept-desc"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief description of this department's focus"
                disabled={submitting}
                rows={2}
              />
            </div>

            <div className="flex gap-2">
              <Button type="submit" disabled={submitting || !name.trim()} size="sm">
                {submitting ? 'Creating...' : 'Create Department'}
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  setShowForm(false);
                  setName('');
                  setDescription('');
                }}
                disabled={submitting}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Department List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {departments.map((dept) => (
          <Card key={dept.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-start gap-3 flex-1">
                <div className="p-2 bg-primary/10 rounded">
                  <Folder className="h-4 w-4 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium mb-1 truncate">{dept.name}</h4>
                  {dept.description && (
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {dept.description}
                    </p>
                  )}
                </div>
              </div>

              {onDeleteDepartment && (
                <button
                  onClick={() => handleDelete(dept.id, dept.name)}
                  className="p-1 hover:bg-destructive/10 rounded text-muted-foreground hover:text-destructive transition-colors"
                  title="Delete department"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </div>

            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Users className="h-3.5 w-3.5" />
              <span>
                {formatNumber(dept.member_count)}{' '}
                {dept.member_count === 1 ? 'member' : 'members'}
              </span>
            </div>
          </Card>
        ))}

        {departments.length === 0 && !showForm && (
          <div className="col-span-full text-center py-12 text-muted-foreground">
            <Folder className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>No departments yet. Create one to organize your team!</p>
          </div>
        )}
      </div>
    </div>
  );
}
