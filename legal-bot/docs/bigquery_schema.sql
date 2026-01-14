-- ============================================
-- LEGALAI BIGQUERY SCHEMA - PROFILE & ACCOUNT SYSTEM
-- ============================================
-- Dataset: legalai
-- Tables: identity_users, user_profiles, user_consent, access_requests
-- Plus existing: conversations, messages, attachments

-- ============================================
-- CREATE DATASET
-- ============================================

CREATE SCHEMA IF NOT EXISTS `legalai`
OPTIONS (
  location = 'US',
  description = 'LegalAI user data and analytics'
);

-- ============================================
-- IDENTITY_USERS TABLE
-- ============================================
-- Maps internal user_id to OAuth identities
-- Stores role, lawyer status, provisioned access control

CREATE TABLE IF NOT EXISTS `legalai.identity_users` (
  user_id STRING NOT NULL,
  auth_provider STRING NOT NULL, -- 'google', 'microsoft', 'email'
  auth_uid STRING NOT NULL, -- Provider's user ID
  email STRING NOT NULL,
  role STRING NOT NULL, -- 'client', 'lawyer', 'employee', 'employee_admin'
  lawyer_status STRING DEFAULT 'not_applicable', -- 'not_applicable', 'pending', 'approved', 'rejected'
  is_provisioned BOOL DEFAULT FALSE, -- LOGIN-ONLY access control
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  last_login_at TIMESTAMP,
  env STRING DEFAULT 'prod', -- 'dev', 'prod' for environment isolation

  -- Primary key and constraints
  PRIMARY KEY (user_id) NOT ENFORCED,

  -- Indexes
  INDEX idx_auth_identity (auth_provider, auth_uid),
  INDEX idx_email (email),
  INDEX idx_role (role),
  INDEX idx_lawyer_status (lawyer_status),
  INDEX idx_provisioned (is_provisioned),
  INDEX idx_created_at (created_at),
  INDEX idx_last_login (last_login_at)
)
OPTIONS (
  description = 'User identity mapping with OAuth providers and access control'
);

-- ============================================
-- USER_PROFILES TABLE
-- ============================================
-- Extended user profile information

CREATE TABLE IF NOT EXISTS `legalai.user_profiles` (
  user_id STRING NOT NULL,
  display_name STRING,
  username STRING, -- Unique username/handle
  avatar_url STRING, -- GCS URL to avatar image
  phone STRING,
  address_line_1 STRING,
  address_line_2 STRING,
  city STRING,
  province_state STRING,
  postal_zip STRING,
  country STRING,
  preferences_json STRING, -- JSON string: theme, font_size, response_style, auto_read, language, legal_tone
  lawyer_status STRING DEFAULT 'not_applicable',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

  -- Primary key and constraints
  PRIMARY KEY (user_id) NOT ENFORCED,

  -- Foreign key reference
  FOREIGN KEY (user_id) REFERENCES `legalai.identity_users`(user_id) NOT ENFORCED,

  -- Indexes
  INDEX idx_username (username),
  INDEX idx_display_name (display_name),
  INDEX idx_updated_at (updated_at)
)
OPTIONS (
  description = 'Extended user profile information and preferences'
);

-- ============================================
-- USER_CONSENT TABLE
-- ============================================
-- Cookie and privacy consent preferences

CREATE TABLE IF NOT EXISTS `legalai.user_consent` (
  user_id STRING NOT NULL,
  necessary BOOL DEFAULT TRUE NOT NULL, -- Always true, required cookies
  analytics BOOL DEFAULT FALSE, -- Analytics cookies
  marketing BOOL DEFAULT FALSE, -- Marketing cookies
  functional BOOL DEFAULT TRUE, -- Functional cookies
  consented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

  -- IP and user agent for audit
  consent_ip STRING,
  consent_user_agent STRING,

  -- Primary key and constraints
  PRIMARY KEY (user_id) NOT ENFORCED,

  -- Foreign key reference
  FOREIGN KEY (user_id) REFERENCES `legalai.identity_users`(user_id) NOT ENFORCED,

  -- Indexes
  INDEX idx_updated_at (updated_at)
)
OPTIONS (
  description = 'User cookie and privacy consent preferences'
);

-- ============================================
-- ACCESS_REQUESTS TABLE
-- ============================================
-- Access requests from non-provisioned users

CREATE TABLE IF NOT EXISTS `legalai.access_requests` (
  id STRING NOT NULL,
  email STRING NOT NULL,
  name STRING,
  requested_role STRING DEFAULT 'client',
  reason STRING,
  organization STRING,
  phone STRING,
  status STRING DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
  reviewed_by_user_id STRING,
  reviewed_at TIMESTAMP,
  reviewer_notes STRING,
  request_ip STRING,
  request_user_agent STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

  -- Primary key
  PRIMARY KEY (id) NOT ENFORCED,

  -- Foreign key references
  FOREIGN KEY (reviewed_by_user_id) REFERENCES `legalai.identity_users`(user_id) NOT ENFORCED,

  -- Indexes
  INDEX idx_email_status (email, status),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at),
  INDEX idx_reviewed_by (reviewed_by_user_id)
)
OPTIONS (
  description = 'Access requests from users not yet provisioned'
);

-- ============================================
-- CONVERSATIONS TABLE (EXISTING - UPDATED)
-- ============================================
-- User-scoped chat conversations

CREATE TABLE IF NOT EXISTS `legalai.conversations` (
  id STRING NOT NULL,
  user_id STRING NOT NULL,
  title STRING,
  law_type STRING,
  jurisdiction_country STRING,
  jurisdiction_region STRING,
  is_archived BOOL DEFAULT FALSE,
  is_pinned BOOL DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  last_message_at TIMESTAMP,

  -- Primary key
  PRIMARY KEY (id) NOT ENFORCED,

  -- Foreign key reference
  FOREIGN KEY (user_id) REFERENCES `legalai.identity_users`(user_id) NOT ENFORCED,

  -- Indexes
  INDEX idx_user_conversations (user_id, updated_at),
  INDEX idx_user_created (user_id, created_at),
  INDEX idx_law_type (law_type),
  INDEX idx_archived (is_archived),
  INDEX idx_pinned (is_pinned)
)
OPTIONS (
  description = 'User-scoped chat conversations'
);

-- ============================================
-- MESSAGES TABLE (EXISTING - UPDATED)
-- ============================================
-- Chat messages within conversations

CREATE TABLE IF NOT EXISTS `legalai.messages` (
  id STRING NOT NULL,
  conversation_id STRING NOT NULL,
  role STRING NOT NULL, -- 'user', 'assistant', 'system'
  content STRING NOT NULL,
  has_attachments BOOL DEFAULT FALSE,
  attachments_json STRING, -- JSON array of attachment metadata
  feedback STRING, -- 'helpful', 'not_helpful'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

  -- Primary key
  PRIMARY KEY (id) NOT ENFORCED,

  -- Foreign key references
  FOREIGN KEY (conversation_id) REFERENCES `legalai.conversations`(id) NOT ENFORCED,

  -- Indexes
  INDEX idx_conversation_messages (conversation_id, created_at),
  INDEX idx_role (role),
  INDEX idx_feedback (feedback)
)
OPTIONS (
  description = 'Chat messages within conversations'
);

-- ============================================
-- ATTACHMENTS TABLE (EXISTING - UPDATED)
-- ============================================
-- Files attached to conversations

CREATE TABLE IF NOT EXISTS `legalai.attachments` (
  id STRING NOT NULL,
  conversation_id STRING NOT NULL,
  filename STRING NOT NULL,
  file_type STRING,
  file_size INT64,
  storage_path STRING NOT NULL, -- GCS path
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  meta_data STRING, -- JSON metadata

  -- Primary key
  PRIMARY KEY (id) NOT ENFORCED,

  -- Foreign key reference
  FOREIGN KEY (conversation_id) REFERENCES `legalai.conversations`(id) NOT ENFORCED,

  -- Indexes
  INDEX idx_conversation_attachments (conversation_id),
  INDEX idx_file_type (file_type)
)
OPTIONS (
  description = 'Files attached to conversations'
);

-- ============================================
-- MERGE UPSERT STATEMENTS
-- ============================================
-- Use these for idempotent inserts/updates

-- IDENTITY_USERS upsert
-- Used when user signs in with OAuth
MERGE `legalai.identity_users` AS target
USING (
  SELECT
    @user_id as user_id,
    @auth_provider as auth_provider,
    @auth_uid as auth_uid,
    @email as email,
    @role as role,
    @lawyer_status as lawyer_status,
    @is_provisioned as is_provisioned,
    @env as env
) AS source
ON target.user_id = source.user_id
WHEN MATCHED THEN
  UPDATE SET
    last_login_at = CURRENT_TIMESTAMP(),
    email = source.email, -- Allow email updates
    role = source.role,
    lawyer_status = source.lawyer_status,
    is_provisioned = source.is_provisioned,
    env = source.env
WHEN NOT MATCHED THEN
  INSERT (user_id, auth_provider, auth_uid, email, role, lawyer_status, is_provisioned, env)
  VALUES (source.user_id, source.auth_provider, source.auth_uid, source.email, source.role, source.lawyer_status, source.is_provisioned, source.env);

-- USER_PROFILES upsert
-- Used when creating/updating user profile
MERGE `legalai.user_profiles` AS target
USING (
  SELECT
    @user_id as user_id,
    @display_name as display_name,
    @username as username,
    @avatar_url as avatar_url,
    @phone as phone,
    @address_line_1 as address_line_1,
    @address_line_2 as address_line_2,
    @city as city,
    @province_state as province_state,
    @postal_zip as postal_zip,
    @country as country,
    @preferences_json as preferences_json,
    @lawyer_status as lawyer_status
) AS source
ON target.user_id = source.user_id
WHEN MATCHED THEN
  UPDATE SET
    display_name = COALESCE(source.display_name, target.display_name),
    username = COALESCE(source.username, target.username),
    avatar_url = COALESCE(source.avatar_url, target.avatar_url),
    phone = COALESCE(source.phone, target.phone),
    address_line_1 = COALESCE(source.address_line_1, target.address_line_1),
    address_line_2 = COALESCE(source.address_line_2, target.address_line_2),
    city = COALESCE(source.city, target.city),
    province_state = COALESCE(source.province_state, target.province_state),
    postal_zip = COALESCE(source.postal_zip, target.postal_zip),
    country = COALESCE(source.country, target.country),
    preferences_json = COALESCE(source.preferences_json, target.preferences_json),
    lawyer_status = COALESCE(source.lawyer_status, target.lawyer_status),
    updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT (user_id, display_name, username, avatar_url, phone, address_line_1, address_line_2, city, province_state, postal_zip, country, preferences_json, lawyer_status)
  VALUES (source.user_id, source.display_name, source.username, source.avatar_url, source.phone, source.address_line_1, source.address_line_2, source.city, source.province_state, source.postal_zip, source.country, source.preferences_json, source.lawyer_status);

-- USER_CONSENT upsert
-- Used when updating consent preferences
MERGE `legalai.user_consent` AS target
USING (
  SELECT
    @user_id as user_id,
    @necessary as necessary,
    @analytics as analytics,
    @marketing as marketing,
    @functional as functional,
    @consent_ip as consent_ip,
    @consent_user_agent as consent_user_agent
) AS source
ON target.user_id = source.user_id
WHEN MATCHED THEN
  UPDATE SET
    necessary = COALESCE(source.necessary, target.necessary),
    analytics = COALESCE(source.analytics, target.analytics),
    marketing = COALESCE(source.marketing, target.marketing),
    functional = COALESCE(source.functional, target.functional),
    consent_ip = COALESCE(source.consent_ip, target.consent_ip),
    consent_user_agent = COALESCE(source.consent_user_agent, target.consent_user_agent),
    updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT (user_id, necessary, analytics, marketing, functional, consent_ip, consent_user_agent)
  VALUES (source.user_id, source.necessary, source.analytics, source.marketing, source.functional, source.consent_ip, source.consent_user_agent);

-- ACCESS_REQUESTS upsert
-- Used when creating access requests
MERGE `legalai.access_requests` AS target
USING (
  SELECT
    @id as id,
    @email as email,
    @name as name,
    @requested_role as requested_role,
    @reason as reason,
    @organization as organization,
    @phone as phone,
    @request_ip as request_ip,
    @request_user_agent as request_user_agent
) AS source
ON target.id = source.id
WHEN MATCHED THEN
  UPDATE SET
    status = 'updated', -- Mark as updated if resubmitted
    updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT (id, email, name, requested_role, reason, organization, phone, request_ip, request_user_agent)
  VALUES (source.id, source.email, source.name, source.requested_role, source.reason, source.organization, source.phone, source.request_ip, source.request_user_agent);

-- ============================================
-- USEFUL QUERIES
-- ============================================

-- Get user by OAuth identity
-- SELECT * FROM `legalai.identity_users`
-- WHERE auth_provider = 'google' AND auth_uid = 'google_user_id';

-- Get user profile with consent
-- SELECT u.*, p.*, c.*
-- FROM `legalai.identity_users` u
-- LEFT JOIN `legalai.user_profiles` p ON u.user_id = p.user_id
-- LEFT JOIN `legalai.user_consent` c ON u.user_id = c.user_id
-- WHERE u.user_id = 'user_id';

-- Get pending access requests
-- SELECT * FROM `legalai.access_requests`
-- WHERE status = 'pending'
-- ORDER BY created_at DESC;

-- Get user conversations with message counts
-- SELECT
--   c.*,
--   COUNT(m.id) as message_count
-- FROM `legalai.conversations` c
-- LEFT JOIN `legalai.messages` m ON c.id = m.conversation_id
-- WHERE c.user_id = 'user_id'
-- GROUP BY c.id, c.user_id, c.title, c.law_type, c.jurisdiction_country,
--          c.jurisdiction_region, c.is_archived, c.is_pinned, c.created_at,
--          c.updated_at, c.last_message_at
-- ORDER BY c.updated_at DESC;

-- ============================================
-- SETUP INSTRUCTIONS
-- ============================================

-- 1. Create the dataset in BigQuery
-- 2. Run this entire SQL file to create all tables
-- 3. Set up Google Cloud Storage bucket for avatars:
--    gsutil mb -p your-project gs://legalai-avatars
--    gsutil iam ch gs://legalai-avatars objectViewer:object public
-- 4. Configure service account with BigQuery and GCS access
-- 5. Set environment variables in your deployment