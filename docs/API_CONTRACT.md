# Receipts API Contract v1

**Version:** 1.0.0  
**Base URL:** `/api/v1`  
**Content-Type:** `application/json`

---

## Authentication

All authenticated endpoints require:
```
Authorization: Bearer <access_token>
```

Access tokens expire in 15 minutes. Use refresh token to obtain new access token.

---

## Error Response Format

All errors follow this structure:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

### Standard Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Missing or invalid auth |
| `FORBIDDEN` | 403 | Not allowed to perform action |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Endpoints

### Health Check

#### `GET /health`
Returns service health status.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-01T12:00:00Z"
}
```

---

### Authentication

#### `POST /auth/register`
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "handle": "username",
  "display_name": "Display Name"
}
```

**Validation:**
- `email`: valid email format, unique
- `password`: min 8 chars, 1 uppercase, 1 lowercase, 1 number
- `handle`: 3-30 chars, alphanumeric + underscore, unique
- `display_name`: 1-100 chars

**Response:** `201 Created`
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "handle": "username",
    "display_name": "Display Name",
    "avatar_url": null,
    "bio": null,
    "created_at": "2026-02-01T12:00:00Z"
  },
  "tokens": {
    "access_token": "jwt_access_token",
    "refresh_token": "jwt_refresh_token",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

---

#### `POST /auth/login`
Authenticate and receive tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "handle": "username",
    "display_name": "Display Name",
    "avatar_url": "https://...",
    "bio": "User bio",
    "created_at": "2026-02-01T12:00:00Z"
  },
  "tokens": {
    "access_token": "jwt_access_token",
    "refresh_token": "jwt_refresh_token",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

---

#### `POST /auth/refresh`
Get new access token using refresh token.

**Request:**
```json
{
  "refresh_token": "jwt_refresh_token"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "new_jwt_access_token",
  "token_type": "Bearer",
  "expires_in": 900
}
```

---

#### `POST /auth/logout`
Invalidate refresh token. **Requires auth.**

**Response:** `204 No Content`

---

#### `GET /auth/me`
Get current authenticated user. **Requires auth.**

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "handle": "username",
  "display_name": "Display Name",
  "avatar_url": "https://...",
  "bio": "User bio",
  "created_at": "2026-02-01T12:00:00Z"
}
```

---

### Users

#### `GET /users/{handle}`
Get public user profile.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "handle": "username",
  "display_name": "Display Name",
  "avatar_url": "https://...",
  "bio": "User bio",
  "receipt_count": 42,
  "created_at": "2026-02-01T12:00:00Z"
}
```

---

#### `PATCH /users/me`
Update current user profile. **Requires auth.**

**Request:**
```json
{
  "display_name": "New Name",
  "bio": "Updated bio",
  "avatar_url": "https://..."
}
```

All fields optional.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "handle": "username",
  "display_name": "New Name",
  "avatar_url": "https://...",
  "bio": "Updated bio",
  "created_at": "2026-02-01T12:00:00Z"
}
```

---

#### `GET /users/{handle}/receipts`
Get user's receipts with pagination.

**Query Parameters:**
- `limit` (int, default 20, max 100)
- `cursor` (string, opaque pagination cursor)

**Response:** `200 OK`
```json
{
  "receipts": [...],
  "pagination": {
    "next_cursor": "cursor_string_or_null",
    "has_more": true
  }
}
```

---

### Receipts

#### `POST /receipts`
Create a new receipt. **Requires auth.**

**Request:**
```json
{
  "claim_text": "The claim being made",
  "claim_type": "text",
  "implication_text": "Why this matters (optional)",
  "topic_ids": ["uuid1", "uuid2"],
  "visibility": "public",
  "evidence": [
    {
      "type": "image",
      "content_uri": "uploads/abc123.png",
      "source_url": "https://original-source.com",
      "captured_at": "2026-02-01T12:00:00Z",
      "caption": "Screenshot of the tweet"
    },
    {
      "type": "link",
      "content_uri": "https://example.com/article",
      "caption": "Supporting article"
    }
  ]
}
```

**Validation:**
- `claim_text`: required, 1-1000 chars
- `claim_type`: enum (text, video_transcript)
- `evidence`: required, 1-10 items
- `visibility`: enum (public, unlisted), default public

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "author": {
    "id": "uuid",
    "handle": "username",
    "display_name": "Display Name",
    "avatar_url": "https://..."
  },
  "claim_text": "The claim being made",
  "claim_type": "text",
  "implication_text": "Why this matters",
  "parent_receipt_id": null,
  "topic_ids": ["uuid1", "uuid2"],
  "visibility": "public",
  "evidence": [
    {
      "id": "uuid",
      "type": "image",
      "content_uri": "uploads/abc123.png",
      "source_url": "https://original-source.com",
      "captured_at": "2026-02-01T12:00:00Z",
      "caption": "Screenshot of the tweet",
      "order_index": 0
    }
  ],
  "reactions": {
    "support": 0,
    "dispute": 0,
    "bookmark": 0
  },
  "fork_count": 0,
  "created_at": "2026-02-01T12:00:00Z"
}
```

---

#### `GET /receipts/{id}`
Get a single receipt by ID.

**Response:** `200 OK`
(Same structure as create response)

---

#### `DELETE /receipts/{id}`
Delete a receipt. **Requires auth.** Only author can delete.

**Response:** `204 No Content`

---

#### `POST /receipts/{id}/fork`
Create a counter-receipt forking an existing receipt. **Requires auth.**

**Request:**
```json
{
  "claim_text": "Counter-claim with evidence",
  "claim_type": "text",
  "implication_text": "Why the original is wrong",
  "evidence": [...]
}
```

**Response:** `201 Created`
(Same structure as create, with `parent_receipt_id` set)

---

#### `GET /receipts/{id}/chain`
Get the full chain of receipts (original + all forks).

**Query Parameters:**
- `depth` (int, default 3, max 10): how many levels of forks to include
- `sort` (string): "relevance" | "chronological" | "reverse_chronological"

**Response:** `200 OK`
```json
{
  "root": {
    "id": "uuid",
    "claim_text": "Original claim",
    "author": {...},
    "evidence": [...],
    "reactions": {...},
    "created_at": "..."
  },
  "forks": [
    {
      "id": "uuid",
      "parent_receipt_id": "root_uuid",
      "claim_text": "Counter claim",
      "author": {...},
      "evidence": [...],
      "reactions": {...},
      "forks": [...],
      "created_at": "..."
    }
  ],
  "total_in_chain": 15
}
```

---

### Evidence

#### `POST /receipts/{id}/evidence`
Add evidence to an existing receipt. **Requires auth.** Only author can add.

**Request:**
```json
{
  "type": "image",
  "content_uri": "uploads/xyz789.png",
  "source_url": "https://...",
  "captured_at": "2026-02-01T12:00:00Z",
  "caption": "Additional evidence"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "type": "image",
  "content_uri": "uploads/xyz789.png",
  "source_url": "https://...",
  "captured_at": "2026-02-01T12:00:00Z",
  "caption": "Additional evidence",
  "order_index": 2,
  "created_at": "2026-02-01T12:00:00Z"
}
```

---

#### `DELETE /receipts/{receipt_id}/evidence/{evidence_id}`
Remove evidence from a receipt. **Requires auth.** Only author can remove. Cannot remove last evidence item.

**Response:** `204 No Content`

---

### Feed

#### `GET /feed`
Get personalized feed. **Requires auth.**

**Query Parameters:**
- `limit` (int, default 20, max 100)
- `cursor` (string)

**Response:** `200 OK`
```json
{
  "receipts": [...],
  "pagination": {
    "next_cursor": "...",
    "has_more": true
  }
}
```

---

#### `GET /feed/trending`
Get trending receipt chains.

**Query Parameters:**
- `limit` (int, default 20, max 100)
- `period` (string): "hour" | "day" | "week" | "month"

**Response:** `200 OK`
```json
{
  "chains": [
    {
      "root_receipt": {...},
      "fork_count": 42,
      "engagement_score": 1250,
      "top_fork": {...}
    }
  ]
}
```

---

#### `GET /feed/topic/{slug}`
Get receipts for a specific topic.

**Query Parameters:**
- `limit` (int, default 20, max 100)
- `cursor` (string)
- `sort` (string): "recent" | "trending"

**Response:** `200 OK`
```json
{
  "topic": {
    "id": "uuid",
    "name": "Politics",
    "slug": "politics",
    "description": "Political accountability"
  },
  "receipts": [...],
  "pagination": {...}
}
```

---

### Topics

#### `GET /topics`
List all topics.

**Response:** `200 OK`
```json
{
  "topics": [
    {
      "id": "uuid",
      "name": "Politics",
      "slug": "politics",
      "description": "Political accountability",
      "receipt_count": 1234
    }
  ]
}
```

---

#### `GET /topics/{slug}`
Get topic details.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "Politics",
  "slug": "politics",
  "description": "Political accountability",
  "receipt_count": 1234
}
```

---

### Reactions

#### `POST /receipts/{id}/reactions`
Add reaction to a receipt. **Requires auth.**

**Request:**
```json
{
  "type": "support"
}
```

**Validation:**
- `type`: enum (support, dispute, bookmark)
- One reaction type per user per receipt

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "receipt_id": "uuid",
  "user_id": "uuid",
  "type": "support",
  "created_at": "..."
}
```

---

#### `DELETE /receipts/{id}/reactions`
Remove user's reaction from a receipt. **Requires auth.**

**Query Parameters:**
- `type` (string, required): which reaction to remove

**Response:** `204 No Content`

---

### Exports

#### `POST /receipts/{id}/export`
Generate exportable receipt card. **Requires auth.**

**Request:**
```json
{
  "format": "image",
  "include_evidence_thumbnails": true,
  "include_chain_preview": false
}
```

**Validation:**
- `format`: enum (image) — video export in v2

**Response:** `202 Accepted`
```json
{
  "export_id": "uuid",
  "status": "processing",
  "estimated_seconds": 5
}
```

---

#### `GET /exports/{export_id}`
Get export status and download URL.

**Response:** `200 OK`
```json
{
  "export_id": "uuid",
  "status": "completed",
  "download_url": "https://...",
  "expires_at": "2026-02-01T13:00:00Z",
  "format": "image",
  "created_at": "..."
}
```

Status values: `processing`, `completed`, `failed`

---

### Moderation

#### `POST /reports`
Report content or user. **Requires auth.**

**Request:**
```json
{
  "target_type": "receipt",
  "target_id": "uuid",
  "reason": "doxxing",
  "details": "Contains personal address information"
}
```

**Validation:**
- `target_type`: enum (receipt, user)
- `reason`: enum (doxxing, harassment, spam, misinformation, other)
- `details`: max 1000 chars

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "target_type": "receipt",
  "target_id": "uuid",
  "reason": "doxxing",
  "status": "pending",
  "created_at": "..."
}
```

---

#### `POST /users/{id}/block`
Block a user. **Requires auth.**

**Response:** `201 Created`
```json
{
  "blocked_user_id": "uuid",
  "created_at": "..."
}
```

---

#### `DELETE /users/{id}/block`
Unblock a user. **Requires auth.**

**Response:** `204 No Content`

---

### Media Upload

#### `POST /uploads`
Get presigned upload URL. **Requires auth.**

**Request:**
```json
{
  "filename": "screenshot.png",
  "content_type": "image/png",
  "size_bytes": 1048576
}
```

**Validation:**
- `content_type`: image/png, image/jpeg, image/gif, image/webp, video/mp4, video/webm
- `size_bytes`: max 50MB for images, 100MB for video

**Response:** `200 OK`
```json
{
  "upload_id": "uuid",
  "upload_url": "https://...",
  "content_uri": "uploads/uuid/screenshot.png",
  "expires_at": "2026-02-01T12:15:00Z"
}
```

---

## Rate Limits

| Endpoint Category | Limit |
|-------------------|-------|
| Auth endpoints | 10/minute |
| Read endpoints | 100/minute |
| Write endpoints | 30/minute |
| Upload endpoints | 10/minute |
| Export endpoints | 5/minute |

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1706788800
```

---

## Pagination

All list endpoints use cursor-based pagination:

```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6IjEyMzQ1In0=",
    "has_more": true
  }
}
```

Pass `cursor` query parameter to get next page.
