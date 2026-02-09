# Enterprise Newsroom - Deployment Guide

## Overview

This guide walks through deploying the Enterprise Newsroom feature to production with zero downtime and zero impact on existing users.

## Pre-Deployment Checklist

### 1. Code Review
- [ ] Review all new database models (`organization.py`, `investigation.py`)
- [ ] Review migrations (`0003_add_organizations.py`, `0004_add_newsroom_receipt_fields.py`)
- [ ] Review API endpoints (`organizations.py`, `investigations.py`)
- [ ] Verify all imports are correct
- [ ] Check that feature flag defaults to `False`

### 2. Environment Variables
Ensure these are set in production environment:
```bash
NEWSROOM_ENABLED=false  # Keep disabled initially
NEWSROOM_BETA_USERS=[]  # Empty array initially
```

### 3. Database Backup
```bash
# Create backup before deployment
# For SQLite:
cp receipts.db receipts.db.backup.$(date +%Y%m%d_%H%M%S)

# For PostgreSQL:
pg_dump receipts_prod > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Deployment Steps

### Phase 1: Backend Deployment (Silent Mode)

**Goal**: Deploy new code and run migrations with feature disabled

#### Step 1.1: Deploy Backend
```bash
cd backend

# Ensure dependencies are installed
pip install -r requirements.txt

# Migrations will run automatically on startup via alembic
# in app/main.py lifespan function
```

#### Step 1.2: Verify Migrations Applied
Check that these tables exist:
- `organizations`
- `departments`
- `organization_members`
- `organization_invites`
- `investigation_threads`

Check that `receipts` table has new columns:
- `organization_id`
- `is_breaking_news`
- `investigation_thread_id`

```bash
# For SQLite:
sqlite3 receipts.db ".schema organizations"
sqlite3 receipts.db "PRAGMA table_info(receipts);"

# For PostgreSQL:
psql receipts_prod -c "\d organizations"
psql receipts_prod -c "\d receipts"
```

#### Step 1.3: Validate Existing Functionality
Test these endpoints to ensure nothing broke:

```bash
# Health check
curl https://your-api.com/health

# Get user profile
curl https://your-api.com/api/v1/users/testhandle

# Get feed
curl https://your-api.com/api/v1/feed

# Create receipt (requires auth)
curl -X POST https://your-api.com/api/v1/receipts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"claim_text": "Test claim", "claim_type": "text"}'
```

**Expected Result**: All existing functionality works identically. Users see no changes.

---

### Phase 2: Beta Testing (After Frontend Complete)

**Goal**: Enable feature for select test users only

#### Step 2.1: Identify Beta Users
Get user IDs of 2-3 test users:
```bash
sqlite3 receipts.db "SELECT id, handle FROM users WHERE handle IN ('testuser1', 'testuser2');"
```

#### Step 2.2: Enable Feature for Beta Users
Update environment variables:
```bash
NEWSROOM_ENABLED=true
NEWSROOM_BETA_USERS=["user-id-1","user-id-2"]
```

Redeploy backend and frontend.

#### Step 2.3: Beta Testing Checklist
- [ ] Beta user can see newsroom UI
- [ ] Platform admin can create organization
- [ ] Platform admin can verify organization
- [ ] Admin can send invitation
- [ ] Beta user can accept invitation
- [ ] Beta user can create department
- [ ] Beta user can create investigation thread
- [ ] Beta user can create receipt with organization
- [ ] Verified badge appears on receipt
- [ ] Regular users see no changes

#### Step 2.4: Monitor Logs
Watch for errors related to:
- Permission checks
- Organization queries
- Investigation creation
- Receipt creation with org fields

---

### Phase 3: General Availability

**Goal**: Open feature to all users

#### Step 3.1: Enable Feature for All
Update environment variables:
```bash
NEWSROOM_ENABLED=true
NEWSROOM_BETA_USERS=[]  # Empty array = open to all
```

Redeploy backend and frontend.

#### Step 3.2: Announce Feature
- Send announcement to users
- Update documentation
- Create tutorial/guide

#### Step 3.3: Monitor
- Error rates
- API response times
- Database query performance
- User adoption metrics

---

## Rollback Procedures

### Scenario A: Migration Fails
**Detection**: App won't start, error in logs
**Action**:
```bash
# Restore database backup
cp receipts.db.backup.TIMESTAMP receipts.db

# Revert to previous deployment
git revert HEAD
# Push and redeploy
```

### Scenario B: Runtime Errors
**Detection**: App starts but endpoints return 500s
**Action**:
```bash
# Set feature flag to false
NEWSROOM_ENABLED=false
# Redeploy

# Investigate logs
# Fix issues
# Redeploy with fix
```

### Scenario C: Beta Issues
**Detection**: Beta users report bugs
**Action**:
```bash
# Disable feature
NEWSROOM_ENABLED=false
# Redeploy

# Data persists, can re-enable after fixes
```

### Scenario D: Full Schema Revert (Last Resort)
**Detection**: Fundamental schema issues
**Action**:
```bash
# Backup current database
cp receipts.db receipts.db.broken

# Restore pre-migration backup
cp receipts.db.backup.TIMESTAMP receipts.db

# Run downgrade migration
cd backend
alembic downgrade 0002_password_reset

# Revert code
git revert HEAD~2  # Revert last 2 commits
# Push and redeploy

# All organization data is lost
# Existing receipts and users preserved
```

---

## Post-Deployment Validation

### Test Suite
Run these tests after each phase:

#### 1. Existing Functionality (Critical)
```bash
# User registration
POST /api/v1/auth/register

# User login
POST /api/v1/auth/login

# Create receipt
POST /api/v1/receipts

# View receipt
GET /api/v1/receipts/{id}

# Get feed
GET /api/v1/feed

# Search
GET /api/v1/search?q=test
```

#### 2. New Endpoints (Beta Only)
```bash
# List organizations
GET /api/v1/organizations

# Create organization (admin only)
POST /api/v1/organizations

# Get organization
GET /api/v1/organizations/{slug}

# Send invitation
POST /api/v1/organizations/{id}/invites

# Accept invitation
POST /api/v1/invites/{token}/accept

# Create investigation
POST /api/v1/investigations

# Create receipt with org
POST /api/v1/receipts
{
  "claim_text": "Test",
  "organization_id": "org-id",
  "is_breaking_news": true
}
```

---

## Performance Considerations

### Database Indexes
All foreign keys have indexes for fast lookups:
- `receipts.organization_id`
- `receipts.investigation_thread_id`
- `organization_members.user_id`
- `organization_members.organization_id`
- `organization_invites.token_hash`

### Query Optimization
Permission checks use early returns and efficient joins:
```python
# Fast check for verified org membership
query = (
    db.query(OrganizationMember)
    .join(OrganizationMember.organization)
    .filter(OrganizationMember.user_id == user.id)
    .filter(OrganizationMember.is_active == True)
    .filter(OrganizationMember.organization.has(is_verified=True))
    .first()
)
```

### Caching Strategy (Future)
Consider caching:
- Organization member lists (cache key: `org:{org_id}:members`)
- User's organization membership (cache key: `user:{user_id}:orgs`)
- Verified badge status (cache key: `user:{user_id}:verified`)

---

## Security Checklist

- [ ] Invitation tokens are hashed (SHA256) before storage
- [ ] Token expiration enforced (default: 7 days)
- [ ] Only platform admins can create organizations
- [ ] Only platform admins can verify organizations
- [ ] Permission checks at every protected endpoint
- [ ] Role-based access control enforced
- [ ] Foreign key constraints prevent orphaned records
- [ ] No sensitive data in logs

---

## Monitoring & Alerts

### Key Metrics to Watch
- API error rate (should not increase)
- API response time (should not increase)
- Database query time (should stay <100ms)
- Organization creation rate
- Invitation acceptance rate
- Investigation creation rate

### Alert Thresholds
- Error rate > 1%: Warning
- Error rate > 5%: Critical
- Response time > 500ms: Warning
- Response time > 1000ms: Critical

### Log Queries
```bash
# Count organization creations
grep "Created organization" app.log | wc -l

# Count invitation acceptances
grep "accepted invite" app.log | wc -l

# Check for permission errors
grep "FORBIDDEN" app.log

# Check for database errors
grep "database" app.log | grep -i error
```

---

## Support & Troubleshooting

### Common Issues

#### Issue: Migration fails with "table already exists"
**Solution**:
```bash
# Check current migration version
alembic current

# If already at head, skip
# If not, manually apply:
alembic upgrade head
```

#### Issue: "Permission denied" errors for all org endpoints
**Solution**:
- Check that organization has `is_verified=true`
- Check that user has active membership
- Check permission logic in `permissions.py`

#### Issue: Frontend shows newsroom features but backend returns 403
**Solution**:
- Verify `NEWSROOM_ENABLED=true` in backend
- Check that user is in `NEWSROOM_BETA_USERS` (if beta mode)
- Restart backend to pick up env var changes

#### Issue: Invitation email not received
**Solution**:
- Check email service configuration
- Verify `invited_by_id` is valid user
- Check invitation token was generated
- TODO: Email service implementation pending

---

## Success Criteria

### Phase 1 (Silent Deployment)
- ✓ Migrations applied successfully
- ✓ Zero errors in logs
- ✓ All existing endpoints work
- ✓ Zero user complaints

### Phase 2 (Beta)
- ✓ Beta users can create orgs
- ✓ Beta users can invite members
- ✓ Verified badges appear
- ✓ Regular users unaffected

### Phase 3 (GA)
- ✓ Feature accessible to all
- ✓ Organizations created
- ✓ Investigations published
- ✓ User adoption growing

---

## Contact & Support

For issues during deployment:
1. Check this guide
2. Review implementation status doc
3. Check migration logs
4. Test endpoints with curl
5. Review error logs
6. Check database state

---

**Last Updated**: 2026-02-08
**Version**: 1.0.0
