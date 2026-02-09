'use client';

import { useEffect } from 'react';
import { Building2 } from 'lucide-react';
import { NewsroomCard } from '@/components/newsroom';
import { useOrganizationStore } from '@/state/organization-store';
import { Spinner } from '@/components/ui/spinner';

export default function NewsroomDirectoryPage() {
  const { organizations, isLoading, loadOrganizationList, error } = useOrganizationStore();

  useEffect(() => {
    loadOrganizationList();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <Building2 className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Newsrooms</h1>
        </div>
        <p className="text-muted-foreground max-w-2xl">
          Verified news organizations using Receipts to publish fact-based journalism
          with evidence.
        </p>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="text-center py-12">
          <p className="text-destructive mb-4">{error}</p>
          <button
            onClick={() => loadOrganizationList()}
            className="text-primary hover:underline"
          >
            Try again
          </button>
        </div>
      )}

      {/* Organizations Grid */}
      {!isLoading && !error && (
        <>
          {organizations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {organizations.map((org) => (
                <NewsroomCard key={org.id} organization={org} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Building2 className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
              <h3 className="text-lg font-medium mb-2">No newsrooms yet</h3>
              <p className="text-muted-foreground">
                Verified news organizations will appear here.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
