'use client';

import { useState } from 'react';
import { ChevronDown, ChevronRight, Mail, MoreVertical } from 'lucide-react';
import type { OrganizationMember, OrganizationRole } from '@/lib/types';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { formatRelativeTime, cn } from '@/lib/utils';

interface TeamRosterProps {
  members: OrganizationMember[];
  isAdmin?: boolean;
  onRoleChange?: (userId: string, newRole: OrganizationRole) => void;
  onRemoveMember?: (userId: string) => void;
}

const roleLabels: Record<OrganizationRole, string> = {
  admin: 'Admin',
  editor: 'Editor',
  senior_reporter: 'Senior Reporter',
  reporter: 'Reporter',
  contributor: 'Contributor',
};

const roleColors: Record<OrganizationRole, 'default' | 'secondary' | 'outline'> = {
  admin: 'default',
  editor: 'secondary',
  senior_reporter: 'secondary',
  reporter: 'outline',
  contributor: 'outline',
};

export function TeamRoster({
  members,
  isAdmin = false,
  onRoleChange,
  onRemoveMember,
}: TeamRosterProps) {
  const [expandedDepts, setExpandedDepts] = useState<Set<string>>(new Set(['no-dept']));

  // Group members by department
  const membersByDept = members.reduce((acc, member) => {
    const deptKey = member.department_id || 'no-dept';
    if (!acc[deptKey]) {
      acc[deptKey] = {
        name: member.department_name || 'General',
        members: [],
      };
    }
    acc[deptKey].members.push(member);
    return acc;
  }, {} as Record<string, { name: string; members: OrganizationMember[] }>);

  const toggleDept = (deptId: string) => {
    setExpandedDepts(prev => {
      const next = new Set(prev);
      if (next.has(deptId)) {
        next.delete(deptId);
      } else {
        next.add(deptId);
      }
      return next;
    });
  };

  return (
    <div className="space-y-4">
      {Object.entries(membersByDept).map(([deptId, dept]) => {
        const isExpanded = expandedDepts.has(deptId);

        return (
          <Card key={deptId} className="overflow-hidden">
            {/* Department Header */}
            <button
              onClick={() => toggleDept(deptId)}
              className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-2">
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                )}
                <h3 className="font-semibold">{dept.name}</h3>
                <Badge variant="secondary" className="ml-2">
                  {dept.members.length}
                </Badge>
              </div>
            </button>

            {/* Members List */}
            {isExpanded && (
              <div className="divide-y">
                {dept.members.map(member => (
                  <MemberRow
                    key={member.user_id}
                    member={member}
                    isAdmin={isAdmin}
                    onRoleChange={onRoleChange}
                    onRemoveMember={onRemoveMember}
                  />
                ))}
              </div>
            )}
          </Card>
        );
      })}
    </div>
  );
}

interface MemberRowProps {
  member: OrganizationMember;
  isAdmin: boolean;
  onRoleChange?: (userId: string, newRole: OrganizationRole) => void;
  onRemoveMember?: (userId: string) => void;
}

function MemberRow({
  member,
  isAdmin,
  onRoleChange,
  onRemoveMember,
}: MemberRowProps) {
  const [showActions, setShowActions] = useState(false);

  return (
    <div className="flex items-center justify-between p-4 hover:bg-muted/30 transition-colors">
      {/* Member Info */}
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <Avatar
          src={member.avatar_url}
          fallback={member.display_name}
          size="sm"
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-medium truncate">{member.display_name}</span>
            <span className="text-sm text-muted-foreground">@{member.handle}</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Joined {formatRelativeTime(member.joined_at)}
          </p>
        </div>
      </div>

      {/* Role Badge */}
      <div className="flex items-center gap-3">
        <Badge variant={roleColors[member.role]}>
          {roleLabels[member.role]}
        </Badge>

        {/* Admin Actions */}
        {isAdmin && (
          <div className="relative">
            <button
              onClick={() => setShowActions(!showActions)}
              className="p-1 hover:bg-muted rounded"
            >
              <MoreVertical className="h-4 w-4 text-muted-foreground" />
            </button>

            {showActions && (
              <div className="absolute right-0 top-8 bg-background border rounded-lg shadow-lg p-2 z-10 min-w-[150px]">
                <button
                  onClick={() => {
                    onRoleChange?.(member.user_id, 'admin');
                    setShowActions(false);
                  }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-muted rounded"
                >
                  Make Admin
                </button>
                <button
                  onClick={() => {
                    onRoleChange?.(member.user_id, 'editor');
                    setShowActions(false);
                  }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-muted rounded"
                >
                  Make Editor
                </button>
                <button
                  onClick={() => {
                    onRoleChange?.(member.user_id, 'reporter');
                    setShowActions(false);
                  }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-muted rounded"
                >
                  Make Reporter
                </button>
                <div className="border-t my-1" />
                <button
                  onClick={() => {
                    if (confirm(`Remove ${member.display_name} from organization?`)) {
                      onRemoveMember?.(member.user_id);
                    }
                    setShowActions(false);
                  }}
                  className="w-full text-left px-3 py-2 text-sm text-destructive hover:bg-destructive/10 rounded"
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
