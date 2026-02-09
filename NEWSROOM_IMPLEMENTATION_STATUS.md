# Enterprise Newsroom Implementation Status

**Date**: 2026-02-08
**Status**: Backend Core Complete (Phase 2A - 60% Complete)

## ✅ Completed Components

### Backend Core Infrastructure

#### 1. Database Models ✓
- **Organization model** (`backend/app/models/db/organization.py`)
  - Organizations with verification flags
  - Departments (newsroom desks)
  - Organization members with roles
  - Organization invites with token-based security

- **Investigation model** (`backend/app/models/db/investigation.py`)
  - Investigation threads for collaborative journalism
  - Links multiple receipts together
  - Publishing workflow

- **Enhanced Receipt model** (`backend/app/models/db/receipt.py`)
  - Added `organization_id` (nullable)
  - Added `is_breaking_news` (nullable)
  - Added `investigation_thread_id` (nullable)

- **Enhanced User model** (`backend/app/models/db/user.py`)
  - Added `organization_memberships` relationship
  - Added `is_newsroom_member` property
  - Added `primary_organization` property

#### 2. Enums ✓
- **OrganizationRole** enum (`backend/app/models/enums.py`)
  - ADMIN, EDITOR, SENIOR_REPORTER, REPORTER, CONTRIBUTOR

#### 3. Database Migrations ✓
- **Migration 0003** (`backend/alembic/versions/0003_add_organizations.py`)
  - Creates organizations table
  - Creates departments table
  - Creates organization_members table
  - Creates organization_invites table
  - Creates investigation_threads table

- **Migration 0004** (`backend/alembic/versions/0004_add_newsroom_receipt_fields.py`)
  - Adds newsroom fields to receipts table (all nullable)

#### 4. Configuration ✓
- **Settings** (`backend/app/core/config.py`)
  - Added `newsroom_enabled` flag (default: False)
  - Added `newsroom_beta_users` list (default: [])

#### 5. Permissions System ✓
- **Permission enum and checker** (`backend/app/core/permissions.py`)
  - Capability-based authorization
  - Permission levels: CREATE_RECEIPT, UPLOAD_ENHANCED, TAG_BREAKING_NEWS, CREATE_INVESTIGATION, VIEW_ADVANCED_ANALYTICS, MANAGE_ORG_SETTINGS, INVITE_MEMBERS, MANAGE_MEMBERS, MANAGE_DEPARTMENTS, MODERATE_CONTENT
  - Dynamic upload limit calculation

#### 6. Services ✓
- **OrganizationService** (`backend/app/services/organization_service.py`)
  - Create/update organizations
  - Create departments
  - Send invitations (with secure token generation)
  - Accept invitations
  - Manage members and roles
  - List organizations, departments, members

- **InvestigationService** (`backend/app/services/investigation_service.py`)
  - Create/update investigation threads
  - Publish investigations
  - Add receipts to investigations
  - List investigation receipts

#### 7. API Endpoints ✓
- **Organizations API** (`backend/app/api/v1/organizations.py`)
  - `GET /organizations` - List verified orgs
  - `POST /organizations` - Create org (admin only)
  - `GET /organizations/{slug}` - Get org details
  - `PATCH /organizations/{org_id}` - Update org settings
  - `GET /organizations/{org_id}/members` - List members
  - `PATCH /organizations/{org_id}/members/{user_id}` - Update member role
  - `DELETE /organizations/{org_id}/members/{user_id}` - Remove member
  - `POST /organizations/{org_id}/invites` - Send invitation
  - `POST /invites/{token}/accept` - Accept invitation
  - `POST /organizations/{org_id}/departments` - Create department
  - `GET /organizations/{org_id}/departments` - List departments

- **Investigations API** (`backend/app/api/v1/investigations.py`)
  - `POST /investigations` - Create investigation
  - `GET /investigations/{id}` - Get investigation details
  - `PATCH /investigations/{id}` - Update investigation
  - `POST /investigations/{id}/publish` - Publish investigation
  - `DELETE /investigations/{id}` - Delete investigation

#### 8. Router Registration ✓
- Added organization and investigation routers to main API router

---

## 🚧 Remaining Backend Work

### Tasks 12-13: Service Updates
- [ ] **Update receipt_service.py** - Handle organization_id, is_breaking_news, investigation_thread_id in receipt creation
- [ ] **Update media_service.py and uploads.py** - Check organization membership for enhanced upload limits (50MB → 200MB)

---

## 🔲 Frontend Implementation (Not Started)

### Required Frontend Work

#### 1. Type Definitions
- [ ] Add Organization, OrganizationMember, Department, Invitation types to `frontend/src/lib/types.ts`
- [ ] Extend User type with organization fields
- [ ] Extend Receipt type with organization fields

#### 2. State Management
- [ ] Extend `frontend/src/state/auth-store.ts` with organization fields
- [ ] Create `frontend/src/state/organization-store.ts` for org state

#### 3. Components
- [ ] Create `VerifiedBadge` component
- [ ] Create `NewsroomCard` component (for directory listing)
- [ ] Create `NewsroomHeader` component (org profile header)
- [ ] Create `TeamRoster` component (member list)
- [ ] Create `InviteForm` component (send invitations)
- [ ] Create `DeskManager` component (department management)
- [ ] Create `DraftList` component (shared drafts)
- [ ] Create `InvestigationThread` component (investigation timeline)
- [ ] Create `AnalyticsDashboard` component (org metrics)
- [ ] Create `OrganizationSettings` component (org settings)

#### 4. Pages
- [ ] Create `/newsroom` - Directory of verified organizations
- [ ] Create `/newsroom/[slug]` - Organization public profile
- [ ] Create `/newsroom/dashboard` - Member dashboard (protected)
- [ ] Create `/newsroom/team` - Team management (admin only)
- [ ] Create `/newsroom/analytics` - Analytics (members only)
- [ ] Create `/newsroom/drafts` - Collaborative drafts (members only)
- [ ] Create `/newsroom/settings` - Organization settings (admin only)
- [ ] Create `/invite/[token]` - Accept invitation

#### 5. Component Updates
- [ ] Update `ReceiptCard` - Add verified badge
- [ ] Update `Header` - Add "Newsrooms" link
- [ ] Update `CreateReceiptForm` - Add newsroom options (org selector, breaking news toggle, investigation thread)

---

## 🧪 Testing Checklist

### Pre-Deployment Testing
- [ ] Run migrations on staging database
- [ ] Test migration downgrade/upgrade cycle
- [ ] Validate all existing endpoints still work
- [ ] Test existing user flows (register, login, create receipt)
- [ ] Verify performance (migrations complete in <5s)

### Post-Deployment Testing
- [ ] Health check responds
- [ ] Existing user login works
- [ ] Receipt creation works
- [ ] Feed loading works
- [ ] Zero increase in error rates

### Beta Testing
- [ ] Beta user can create organization
- [ ] Beta user can send invitations
- [ ] Invitation acceptance flow works
- [ ] Permission system enforces boundaries
- [ ] Regular users unchanged

---

## 📋 Deployment Steps

### Phase 1: Silent Deployment (Backend Only)

1. **Set environment variables** (keep feature disabled):
   ```bash
   NEWSROOM_ENABLED=false
   NEWSROOM_BETA_USERS=[]
   ```

2. **Deploy backend**:
   ```bash
   cd backend
   # Migrations will run automatically on startup
   # Deploy to production
   ```

3. **Validate**:
   - All existing endpoints work
   - User registration/login work
   - Receipt creation/viewing work
   - Zero visible changes to users

### Phase 2: Beta Activation (After Frontend Complete)

1. **Enable for beta users**:
   ```bash
   NEWSROOM_ENABLED=true
   NEWSROOM_BETA_USERS=["user-id-1","user-id-2"]
   ```

2. **Deploy frontend** with newsroom UI

3. **Validate**:
   - Beta users see newsroom features
   - Regular users see zero changes

### Phase 3: General Availability

1. **Open to all users**:
   ```bash
   NEWSROOM_ENABLED=true
   NEWSROOM_BETA_USERS=[]
   ```

2. **Monitor**:
   - Error rates
   - Performance
   - User adoption

---

## 🔑 Key Design Decisions

### Backward Compatibility
- All new database columns are nullable
- Existing receipts get NULL for organization fields
- Existing users automatically work without org membership
- No breaking changes to existing API responses

### Security
- Invitation tokens are hashed (SHA256) before storage
- Only platform admins can create organizations
- Only platform admins can verify organizations
- Permission checks at every endpoint
- Role-based access control within organizations

### Performance
- Denormalized counts (receipt_count, member_count) for fast queries
- Indexes on all foreign keys
- Efficient permission checking with early returns

### Flexibility
- Feature flag control for gradual rollout
- Beta user list for controlled testing
- Organization capabilities configurable per-org

---

## 📁 Files Created

### Backend
```
backend/app/models/db/organization.py
backend/app/models/db/investigation.py
backend/app/core/permissions.py
backend/app/services/organization_service.py
backend/app/services/investigation_service.py
backend/app/api/v1/organizations.py
backend/app/api/v1/investigations.py
backend/alembic/versions/0003_add_organizations.py
backend/alembic/versions/0004_add_newsroom_receipt_fields.py
```

### Backend Modified
```
backend/app/models/enums.py (added OrganizationRole)
backend/app/models/db/__init__.py (exported new models)
backend/app/models/db/user.py (added org relationships)
backend/app/models/db/receipt.py (added org fields)
backend/app/core/config.py (added newsroom settings)
backend/app/api/v1/router.py (registered new routers)
```

---

## 🚀 Next Steps

1. **Complete remaining backend tasks** (receipt_service, media_service updates)
2. **Implement frontend** (types, state, components, pages)
3. **Write integration tests** for new endpoints
4. **Test migration on staging** database
5. **Deploy backend** with `NEWSROOM_ENABLED=false`
6. **Validate existing functionality** unchanged
7. **Deploy frontend** with newsroom UI
8. **Enable beta** for test users
9. **Monitor and iterate** based on feedback
10. **Launch to general availability**

---

## ⚠️ Important Notes

- **Do not enable newsroom features in production until frontend is complete**
- **Always test migrations on a database backup first**
- **Monitor error logs closely during beta period**
- **Regular users should see ZERO changes until feature is enabled**
- **Only platform moderators (admins) can create and verify organizations**

---

## 📞 Support

For issues or questions about this implementation:
- Review this document
- Check migration logs in Vercel/backend console
- Test endpoints with Postman/curl
- Review permission checks in `permissions.py`
