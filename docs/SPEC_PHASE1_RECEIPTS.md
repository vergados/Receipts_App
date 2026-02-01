# Receipts App — Phase 1 Frozen Specification

**Status:** FROZEN  
**Created:** 2026-02-01  
**Source:** ChatGPT 5.2 (Thinking/Design Phase)  
**Executor:** Claude Opus 4.5 (Implementation Phase)

---

## Mission Statement

Receipts is a proof-first short-form social platform where the basic post type is **Claim → Evidence → Implication**. It turns accountability into a shareable format: users can attach screenshots, links, and time-stamped context; others can fork the post with counter-receipts; and the system preserves the chain so conversations converge toward clarity instead of endless noise.

---

## Core Features (v1)

### 1. Receipt Post Creation
- Every post is a "Receipt" containing:
  - **Claim** (required): text or transcript
  - **Evidence** (required, 1+): attachments proving the claim
  - **Implication** (optional): what this means / why it matters
- Creation target: < 60 seconds

### 2. Evidence Attachments
Supported types:
- Image/Screenshot
- Link URL
- Short video clip
- Text quote (with source attribution)

Each evidence item includes:
- Type identifier
- Content URI
- Source URL (optional)
- Capture timestamp
- Caption (optional)

### 3. Fork/Counter-Receipt
- Any receipt can be "forked" to create a counter-receipt
- Fork must reference exactly one parent receipt
- Forks inherit chain context
- Counter creation target: < 30 seconds

### 4. Receipt Chain View
- Shows original receipt + all forks
- Displays lineage clearly
- Sorted by relevance (engagement signals)

### 5. Home Feed
- Browse by topic tabs
- Trending chains section
- Recent receipts
- Personalized (later versions)

### 6. Export/Share Receipt Card
- Generate clean visual card containing:
  - Claim text
  - Evidence thumbnails
  - Timestamp
  - Author handle
- Exportable as image
- Shareable outside the app

### 7. Accounts & Profiles
- User registration/login
- Handle (unique username)
- Avatar
- Profile bio
- User's receipts list
- Pinned receipts

### 8. Basic Moderation
- Report content (with reason)
- Block users
- Admin takedown workflow
- Anti-doxxing enforcement

### 9. Accessibility
- Image captions/alt text
- Screen reader labels
- Large text support

---

## Non-Features (Explicitly Out of Scope for v1)

- ❌ Truth scoring / political labeling
- ❌ Full DM/messaging system
- ❌ Marketplace / payments
- ❌ Long-form video platform
- ❌ External platform API integrations
- ❌ Algorithm transparency panel (v2)
- ❌ Evidence archiving (v2)
- ❌ Collections/case files (v2)
- ❌ Collaborative chains (v2)

---

## Data Entities

### User
- id (UUID)
- handle (unique)
- email
- password_hash
- display_name
- avatar_url
- bio
- created_at
- updated_at

### Receipt
- id (UUID)
- author_id (FK → User)
- claim_text (required)
- claim_type (enum: text, video_transcript)
- implication_text (optional)
- parent_receipt_id (FK → Receipt, nullable for originals)
- topic_ids (many-to-many)
- visibility (enum: public, unlisted)
- created_at
- updated_at

### EvidenceItem
- id (UUID)
- receipt_id (FK → Receipt)
- type (enum: image, link, video, quote)
- content_uri (storage path or URL)
- source_url (optional, for attribution)
- captured_at (timestamp)
- caption (optional)
- order_index (for display ordering)
- created_at

### Topic
- id (UUID)
- name (unique)
- slug (unique)
- description
- created_at

### Reaction
- id (UUID)
- receipt_id (FK → Receipt)
- user_id (FK → User)
- type (enum: support, dispute, bookmark)
- created_at

### Report
- id (UUID)
- reporter_id (FK → User)
- target_type (enum: receipt, user)
- target_id (UUID)
- reason (enum: doxxing, harassment, spam, misinformation, other)
- details (text)
- status (enum: pending, reviewed, actioned, dismissed)
- created_at
- reviewed_at

### ModerationAction
- id (UUID)
- report_id (FK → Report, nullable)
- moderator_id (FK → User)
- action_type (enum: warning, content_removal, user_ban, user_suspension)
- target_type (enum: receipt, user)
- target_id (UUID)
- reason (text)
- created_at

---

## API Contracts (v1)

### Authentication
```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
GET  /api/v1/auth/me
```

### Users
```
GET    /api/v1/users/{handle}
PATCH  /api/v1/users/me
GET    /api/v1/users/{handle}/receipts
```

### Receipts
```
POST   /api/v1/receipts
GET    /api/v1/receipts/{id}
DELETE /api/v1/receipts/{id}
POST   /api/v1/receipts/{id}/fork
GET    /api/v1/receipts/{id}/chain
```

### Evidence
```
POST   /api/v1/receipts/{id}/evidence
DELETE /api/v1/receipts/{id}/evidence/{evidence_id}
```

### Feed
```
GET    /api/v1/feed
GET    /api/v1/feed/trending
GET    /api/v1/feed/topic/{slug}
```

### Topics
```
GET    /api/v1/topics
GET    /api/v1/topics/{slug}
```

### Reactions
```
POST   /api/v1/receipts/{id}/reactions
DELETE /api/v1/receipts/{id}/reactions
```

### Exports
```
POST   /api/v1/receipts/{id}/export
GET    /api/v1/exports/{export_id}
```

### Moderation
```
POST   /api/v1/reports
GET    /api/v1/users/{id}/block
DELETE /api/v1/users/{id}/block
```

---

## Technical Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+ / FastAPI |
| Database | PostgreSQL (prod) / SQLite (dev) |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | JWT (access + refresh tokens) |
| Storage | Local filesystem (dev) / S3-compatible (prod) |
| Frontend | React 18 / Next.js 14 |
| Styling | Tailwind CSS |
| State | Zustand or React Query |
| Desktop | Tauri (add-on) |
| Apple | SwiftUI shells (add-on) |

---

## Architecture Rules

1. **All business logic lives in `backend/app/services/`**
2. UI shells (web/desktop/apple) only call APIs and render state
3. No core logic in API route handlers — they delegate to services
4. Services are the only layer that touches repositories
5. Repositories are the only layer that touches the database

---

## Success Criteria (v1)

- [ ] Create receipt in < 60 seconds
- [ ] Create counter-receipt in < 30 seconds
- [ ] Receipt cards export cleanly
- [ ] Chains display with clear lineage
- [ ] Basic moderation prevents abuse escalation
- [ ] All core API endpoints functional
- [ ] Frontend renders all core screens
- [ ] Tests pass for critical paths

---

## Build Phases

### Phase 1: v1 MVP (This Build)
- Receipts, evidence, forks
- Feed, chain view
- Export receipt cards
- Basic moderation

### Phase 2: v2 (Future)
- Algorithm transparency panel
- Collections/case files
- Evidence archiving
- Better search

### Phase 3: v3 (Future)
- Creator monetization
- Collaborative chains
- Advanced redaction
- Enterprise exports
