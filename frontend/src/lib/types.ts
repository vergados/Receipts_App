// Enums
export type ClaimType = 'text' | 'video_transcript';
export type EvidenceType = 'image' | 'link' | 'video' | 'quote';
export type Visibility = 'public' | 'unlisted';
export type ReactionType = 'support' | 'dispute' | 'bookmark';
export type ReportReason = 'doxxing' | 'harassment' | 'spam' | 'misinformation' | 'other';
export type ReportStatus = 'pending' | 'reviewed' | 'actioned' | 'dismissed';
export type TargetType = 'receipt' | 'user';
export type ExportStatus = 'processing' | 'completed' | 'failed';
export type ExportFormat = 'image';
export type NotificationType = 'receipt_support' | 'receipt_dispute' | 'receipt_counter' | 'receipt_bookmark' | 'new_follower' | 'mention';

// User types
export interface UserPublic {
  id: string;
  handle: string;
  display_name: string;
  avatar_url: string | null;
  bio: string | null;
  receipt_count: number;
  created_at: string;
}

export interface UserPrivate extends UserPublic {
  email: string;
  is_verified: boolean;
  is_moderator: boolean;
  updated_at: string | null;
  last_login_at: string | null;
}

export interface AuthorSummary {
  id: string;
  handle: string;
  display_name: string;
  avatar_url: string | null;
}

// Evidence types
export interface EvidenceItem {
  id: string;
  type: EvidenceType;
  content_uri: string;
  source_url: string | null;
  captured_at: string | null;
  caption: string | null;
  order_index: number;
  created_at: string;
}

export interface EvidenceCreate {
  type: EvidenceType;
  content_uri: string;
  source_url?: string | null;
  captured_at?: string | null;
  caption?: string | null;
}

// Reaction types
export interface ReactionCounts {
  support: number;
  dispute: number;
  bookmark: number;
}

// Receipt types
export interface Receipt {
  id: string;
  author: AuthorSummary;
  claim_text: string;
  claim_type: ClaimType;
  implication_text: string | null;
  parent_receipt_id: string | null;
  topic_ids: string[];
  visibility: Visibility;
  evidence: EvidenceItem[];
  reactions: ReactionCounts;
  fork_count: number;
  created_at: string;
  updated_at: string | null;
}

export interface ReceiptSummary {
  id: string;
  author: AuthorSummary;
  claim_text: string;
  evidence_count: number;
  reactions: ReactionCounts;
  fork_count: number;
  created_at: string;
}

export interface ReceiptCreate {
  claim_text: string;
  claim_type?: ClaimType;
  implication_text?: string | null;
  topic_ids?: string[];
  visibility?: Visibility;
  evidence: EvidenceCreate[];
}

export interface ReceiptFork {
  claim_text: string;
  claim_type?: ClaimType;
  implication_text?: string | null;
  evidence: EvidenceCreate[];
}

export interface ReceiptChainNode {
  id: string;
  parent_receipt_id: string;
  claim_text: string;
  author: AuthorSummary;
  evidence: EvidenceItem[];
  reactions: ReactionCounts;
  forks: ReceiptChainNode[];
  created_at: string;
}

export interface ReceiptChain {
  root: Receipt;
  forks: ReceiptChainNode[];
  total_in_chain: number;
}

// Topic types
export interface Topic {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  receipt_count: number;
  created_at: string;
}

// Feed types
export interface TrendingChain {
  root_receipt: ReceiptSummary;
  fork_count: number;
  engagement_score: number;
  top_fork: ReceiptSummary | null;
}

// Pagination
export interface PaginationInfo {
  next_cursor: string | null;
  has_more: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationInfo;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  handle: string;
  display_name: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: UserPrivate;
  tokens: TokenResponse;
}

// Report types
export interface ReportCreate {
  target_type: TargetType;
  target_id: string;
  reason: ReportReason;
  details?: string | null;
}

export interface Report {
  id: string;
  target_type: TargetType;
  target_id: string;
  reason: ReportReason;
  status: ReportStatus;
  details: string | null;
  created_at: string;
}

// Export types
export interface ExportCreate {
  format?: ExportFormat;
  include_evidence_thumbnails?: boolean;
  include_chain_preview?: boolean;
}

export interface ExportResponse {
  export_id: string;
  status: ExportStatus;
  estimated_seconds: number | null;
  download_url: string | null;
  expires_at: string | null;
  format: ExportFormat;
  error_message: string | null;
  created_at: string;
}

// Upload types
export interface UploadRequest {
  filename: string;
  content_type: string;
  size_bytes: number;
}

export interface UploadResponse {
  upload_id: string;
  upload_url: string;
  content_uri: string;
  expires_at: string;
}

// API Response types
export interface ReceiptListResponse {
  receipts: Receipt[];
  pagination: PaginationInfo;
}

export interface TopicListResponse {
  topics: Topic[];
}

export interface FeedResponse {
  receipts: Receipt[];
  pagination: PaginationInfo;
}

export interface TrendingResponse {
  chains: TrendingChain[];
}

export interface TopicFeedResponse {
  topic: Topic;
  receipts: Receipt[];
  pagination: PaginationInfo;
}

// Notification types
export interface NotificationActor {
  id: string;
  handle: string;
  display_name: string;
  avatar_url: string | null;
}

export interface NotificationReceipt {
  id: string;
  claim_text: string;
}

export interface Notification {
  id: string;
  type: NotificationType;
  is_read: boolean;
  actor: NotificationActor | null;
  receipt: NotificationReceipt | null;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: Notification[];
  total: number;
  unread_count: number;
}

// Admin types
export type ModerationActionType = 'warning' | 'content_removal' | 'user_ban' | 'user_suspension';

export interface AdminStats {
  total_users: number;
  total_receipts: number;
  pending_reports: number;
  total_reports: number;
  actions_today: number;
  active_users_today: number;
}

export interface ReporterSummary {
  id: string;
  handle: string;
  display_name: string;
}

export interface TargetUserSummary {
  id: string;
  handle: string;
  display_name: string;
  avatar_url: string | null;
  is_active: boolean;
}

export interface TargetReceiptSummary {
  id: string;
  claim_text: string;
  author_handle: string;
}

export interface AdminReport {
  id: string;
  target_type: TargetType;
  target_id: string;
  reason: ReportReason;
  status: ReportStatus;
  details: string | null;
  reporter: ReporterSummary;
  target_user: TargetUserSummary | null;
  target_receipt: TargetReceiptSummary | null;
  reviewed_at: string | null;
  created_at: string;
}

export interface AdminReportList {
  reports: AdminReport[];
  total: number;
  pending_count: number;
}

export interface ModeratorSummary {
  id: string;
  handle: string;
  display_name: string;
}

export interface ModerationAction {
  id: string;
  action_type: ModerationActionType;
  target_type: TargetType;
  target_id: string;
  reason: string;
  moderator: ModeratorSummary;
  report_id: string | null;
  created_at: string;
}

export interface ModerationActionList {
  actions: ModerationAction[];
  total: number;
}

export interface AdminUser {
  id: string;
  handle: string;
  display_name: string;
  email: string;
  avatar_url: string | null;
  bio: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_moderator: boolean;
  receipt_count: number;
  report_count: number;
  last_login_at: string | null;
  created_at: string;
}

export interface AdminUserList {
  users: AdminUser[];
  total: number;
}
