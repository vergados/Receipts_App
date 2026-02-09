# Organization State Store - Usage Guide

## Overview

The organization state store (`organization-store.ts`) manages all newsroom-related state using Zustand with persistence. It handles organizations, members, departments, invitations, and investigations.

---

## Features

### ✅ State Management
- Current user's organization (if member)
- Organization directory (all verified orgs)
- Members and departments
- Investigation threads
- Loading and error states

### ✅ Persistence
- Current organization cached
- Organization list cached
- Department list cached
- Auto-rehydrates on page reload

### ✅ Integration
- Auto-initializes when user logs in
- Auto-clears when user logs out
- Syncs with auth store

---

## Basic Usage

### Import the Store

```tsx
import { useOrganizationStore } from '@/state/organization-store';

// Or use selector hooks
import {
  useCurrentOrganization,
  useIsOrgMember,
  useOrganizations,
  useCurrentOrgMembers,
  useCurrentOrgDepartments,
} from '@/state/organization-store';
```

### Check if User is Organization Member

```tsx
function MyComponent() {
  const isOrgMember = useIsOrgMember();
  const currentOrg = useCurrentOrganization();

  if (!isOrgMember) {
    return <div>Not a member of any organization</div>;
  }

  return <div>Member of {currentOrg?.name}</div>;
}
```

### Load Organization List (Directory)

```tsx
function NewsroomDirectory() {
  const { organizations, isLoading, loadOrganizationList } = useOrganizationStore();

  useEffect(() => {
    loadOrganizationList();
  }, []);

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {organizations.map(org => (
        <OrganizationCard key={org.id} org={org} />
      ))}
    </div>
  );
}
```

---

## Organization Management

### Get Organization by Slug

```tsx
function OrganizationProfile({ slug }: { slug: string }) {
  const { getOrganization, isLoading } = useOrganizationStore();
  const [org, setOrg] = useState<Organization | null>(null);

  useEffect(() => {
    getOrganization(slug).then(setOrg).catch(console.error);
  }, [slug]);

  if (isLoading) return <div>Loading...</div>;
  if (!org) return <div>Organization not found</div>;

  return (
    <div>
      <h1>{org.name}</h1>
      <p>{org.description}</p>
    </div>
  );
}
```

### Create Organization (Admin Only)

```tsx
function CreateOrgForm() {
  const { createOrganization, isLoading, error } = useOrganizationStore();

  const handleSubmit = async (data: OrganizationCreate) => {
    try {
      const newOrg = await createOrganization(data);
      console.log('Created:', newOrg);
      router.push(`/newsroom/${newOrg.slug}`);
    } catch (err) {
      console.error('Failed to create org:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      {/* Form fields */}
    </form>
  );
}
```

### Update Organization Settings

```tsx
function OrganizationSettings() {
  const { currentOrganization, updateOrganization } = useOrganizationStore();

  const handleUpdate = async (data: OrganizationUpdate) => {
    if (!currentOrganization) return;

    try {
      await updateOrganization(currentOrganization.id, data);
      toast.success('Settings updated');
    } catch (err) {
      toast.error('Failed to update settings');
    }
  };

  return <SettingsForm onSubmit={handleUpdate} />;
}
```

---

## Member Management

### Load and Display Members

```tsx
function TeamRoster() {
  const {
    currentOrgMembers,
    isLoadingMembers,
    loadCurrentOrgMembers,
  } = useOrganizationStore();

  useEffect(() => {
    loadCurrentOrgMembers();
  }, []);

  if (isLoadingMembers) return <div>Loading members...</div>;

  return (
    <div>
      {currentOrgMembers.map(member => (
        <MemberCard key={member.user_id} member={member} />
      ))}
    </div>
  );
}
```

### Update Member Role

```tsx
function MemberRoleDropdown({ orgId, userId, currentRole }: Props) {
  const { updateMemberRole } = useOrganizationStore();

  const handleRoleChange = async (newRole: OrganizationRole) => {
    try {
      await updateMemberRole(orgId, userId, { role: newRole });
      toast.success('Role updated');
    } catch (err) {
      toast.error('Failed to update role');
    }
  };

  return (
    <select value={currentRole} onChange={(e) => handleRoleChange(e.target.value)}>
      <option value="admin">Admin</option>
      <option value="editor">Editor</option>
      <option value="senior_reporter">Senior Reporter</option>
      <option value="reporter">Reporter</option>
      <option value="contributor">Contributor</option>
    </select>
  );
}
```

### Remove Member

```tsx
function RemoveMemberButton({ orgId, userId }: Props) {
  const { removeMember } = useOrganizationStore();

  const handleRemove = async () => {
    if (!confirm('Remove this member?')) return;

    try {
      await removeMember(orgId, userId);
      toast.success('Member removed');
    } catch (err) {
      toast.error('Failed to remove member');
    }
  };

  return <button onClick={handleRemove}>Remove</button>;
}
```

---

## Department Management

### Load and Display Departments

```tsx
function DepartmentList() {
  const {
    currentOrgDepartments,
    isLoadingDepartments,
    loadCurrentOrgDepartments,
  } = useOrganizationStore();

  useEffect(() => {
    loadCurrentOrgDepartments();
  }, []);

  if (isLoadingDepartments) return <div>Loading...</div>;

  return (
    <div>
      {currentOrgDepartments.map(dept => (
        <DepartmentCard key={dept.id} dept={dept} />
      ))}
    </div>
  );
}
```

### Create Department

```tsx
function CreateDepartmentForm({ orgId }: { orgId: string }) {
  const { createDepartment } = useOrganizationStore();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    try {
      await createDepartment(orgId, { name, description });
      toast.success('Department created');
      setName('');
      setDescription('');
    } catch (err) {
      toast.error('Failed to create department');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Department name"
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
      />
      <button type="submit">Create Department</button>
    </form>
  );
}
```

---

## Invitation Management

### Send Invitation

```tsx
function InviteForm({ orgId }: { orgId: string }) {
  const { sendInvitation } = useOrganizationStore();
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<OrganizationRole>('reporter');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    try {
      const invite = await sendInvitation(orgId, { email, role });
      toast.success(`Invitation sent to ${email}`);
      // TODO: Copy invite link or send email
      console.log('Invite token:', invite.id);
      setEmail('');
    } catch (err) {
      toast.error('Failed to send invitation');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email address"
      />
      <select value={role} onChange={(e) => setRole(e.target.value as OrganizationRole)}>
        <option value="reporter">Reporter</option>
        <option value="editor">Editor</option>
        <option value="admin">Admin</option>
      </select>
      <button type="submit">Send Invitation</button>
    </form>
  );
}
```

### Accept Invitation

```tsx
function AcceptInvitePage({ token }: { token: string }) {
  const { acceptInvitation, isLoading, error } = useOrganizationStore();
  const router = useRouter();

  const handleAccept = async () => {
    try {
      await acceptInvitation(token);
      toast.success('Welcome to the organization!');
      router.push('/newsroom/dashboard');
    } catch (err) {
      toast.error('Invalid or expired invitation');
    }
  };

  return (
    <div>
      <h1>You've been invited!</h1>
      {error && <div className="error">{error}</div>}
      <button onClick={handleAccept} disabled={isLoading}>
        {isLoading ? 'Accepting...' : 'Accept Invitation'}
      </button>
    </div>
  );
}
```

---

## Investigation Management

### Create Investigation Thread

```tsx
function CreateInvestigationForm() {
  const { currentOrganization, createInvestigation } = useOrganizationStore();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!currentOrganization) return;

    try {
      const investigation = await createInvestigation({
        organization_id: currentOrganization.id,
        title,
        description,
      });
      toast.success('Investigation created');
      router.push(`/investigations/${investigation.id}`);
    } catch (err) {
      toast.error('Failed to create investigation');
    }
  };

  return <form onSubmit={handleSubmit}>{/* Form fields */}</form>;
}
```

### Publish Investigation

```tsx
function PublishInvestigationButton({ investigationId }: { investigationId: string }) {
  const { publishInvestigation } = useOrganizationStore();

  const handlePublish = async () => {
    if (!confirm('Publish this investigation?')) return;

    try {
      await publishInvestigation(investigationId);
      toast.success('Investigation published');
    } catch (err) {
      toast.error('Failed to publish');
    }
  };

  return <button onClick={handlePublish}>Publish</button>;
}
```

---

## Error Handling

### Display and Clear Errors

```tsx
function ErrorAlert() {
  const { error, clearError } = useOrganizationStore();

  if (!error) return null;

  return (
    <div className="alert alert-error">
      <p>{error}</p>
      <button onClick={clearError}>Dismiss</button>
    </div>
  );
}
```

---

## Advanced Usage

### Custom Selector Hook

```tsx
// Get only admin members
export const useOrgAdmins = () =>
  useOrganizationStore((state) =>
    state.currentOrgMembers.filter(m => m.role === 'admin')
  );

// Get department by ID
export const useDepartment = (deptId: string) =>
  useOrganizationStore((state) =>
    state.currentOrgDepartments.find(d => d.id === deptId)
  );
```

### Conditional Loading

```tsx
function ConditionalLoader() {
  const {
    isLoading,
    isLoadingMembers,
    isLoadingDepartments,
    isLoadingInvestigations,
  } = useOrganizationStore();

  if (isLoading || isLoadingMembers || isLoadingDepartments) {
    return <Spinner />;
  }

  return <Content />;
}
```

---

## Integration with Auth

The organization store **automatically initializes** when a user logs in:

```tsx
// In your app initialization
import { useAuthInit } from '@/state/auth-store';

function App() {
  const checkAuth = useAuthInit();

  useEffect(() => {
    checkAuth(); // This will also initialize organization data if user is a member
  }, []);

  return <YourApp />;
}
```

No manual initialization needed! The store:
- ✅ Loads organization data on login
- ✅ Loads organization data on page refresh (if user is authenticated)
- ✅ Clears organization data on logout

---

## Best Practices

### 1. Use Selector Hooks
```tsx
// ✅ Good - Only re-renders when currentOrganization changes
const currentOrg = useCurrentOrganization();

// ❌ Bad - Re-renders on any state change
const { currentOrganization } = useOrganizationStore();
```

### 2. Handle Loading States
```tsx
const { isLoading, error } = useOrganizationStore();

if (isLoading) return <Spinner />;
if (error) return <ErrorMessage error={error} />;
```

### 3. Error Handling
```tsx
try {
  await createOrganization(data);
  toast.success('Success');
} catch (err) {
  // Error is already set in store
  // Just show user feedback
  toast.error('Failed to create organization');
}
```

### 4. Cleanup on Unmount
```tsx
useEffect(() => {
  loadCurrentOrgMembers();

  return () => {
    // Clear error on unmount
    clearError();
  };
}, []);
```

---

## Persisted State

The following state is persisted to localStorage:
- `currentOrganization`
- `organizations` (directory cache)
- `currentOrgDepartments`

Everything else is session-only and cleared on page refresh.

---

## API Integration

The store automatically integrates with your API client:

```tsx
// It uses dynamic imports to avoid circular dependencies
const { apiClient } = await import('@/lib/api-client');
const response = await apiClient.get('/organizations');
```

All API calls include:
- Automatic authentication (via api-client)
- Error handling
- Loading state management
- Optimistic updates where applicable

---

## TypeScript Support

Full TypeScript support with:
- ✅ Type-safe actions
- ✅ Type-safe selectors
- ✅ Type-safe hooks
- ✅ IntelliSense everywhere

```tsx
// TypeScript knows the exact type
const org: Organization | null = useCurrentOrganization();
const members: OrganizationMember[] = useCurrentOrgMembers();
```

---

## Summary

The organization store provides:
- 🔄 **Automatic sync** with auth
- 💾 **Smart persistence** for critical data
- 🎯 **Type-safe** operations
- ⚡ **Optimized** re-renders
- 🛡️ **Error handling** built-in
- 🔌 **Easy integration** with components

Use it to build powerful newsroom features with minimal boilerplate! 🚀
