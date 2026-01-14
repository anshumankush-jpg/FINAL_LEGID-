-- ============================================
-- LEGALAI BIGQUERY SCHEMA
-- Dataset: legalai
-- ============================================

-- Create dataset (run once)
-- CREATE SCHEMA IF NOT EXISTS `your-project-id.legalai`;

-- ============================================
-- TABLE: identity_users
-- Core user identity and authentication mapping
-- ============================================
CREATE TABLE IF NOT EXISTS `legalai.identity_users` (
  user_id STRING NOT NULL,                    -- Internal UUID (stable)
  auth_provider STRING NOT NULL,              -- google | microsoft | email
  auth_uid STRING NOT NULL,                   -- Provider's user ID
  email STRING NOT NULL,                      -- User email
  role STRING NOT NULL DEFAULT 'client',      -- client | lawyer | employee | employee_admin
  lawyer_status STRING DEFAULT 'not_applicable', -- not_applicable | pending | approved | rejected
  is_provisioned BOOL DEFAULT FALSE,          -- Whether user can access the app
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  last_login_at TIMESTAMP,
  env STRING DEFAULT 'dev'                    -- dev | prod
)
OPTIONS (
  description = 'Core user identity table mapping auth providers to internal user IDs'
);

-- Upsert for identity_users (MERGE statement)
-- Use this when creating/updating users
/*
MERGE `legalai.identity_users` AS target
USING (
  SELECT 
    @user_id AS user_id,
    @auth_provider AS auth_provider,
    @auth_uid AS auth_uid,
    @email AS email,
    @role AS role,
    @lawyer_status AS lawyer_status,
    @is_provisioned AS is_provisioned,
    @env AS env
) AS source
ON target.auth_uid = source.auth_uid AND target.auth_provider = source.auth_provider
WHEN MATCHED THEN
  UPDATE SET
    email = source.email,
    role = source.role,
    lawyer_status = source.lawyer_status,
    is_provisioned = source.is_provisioned,
    last_login_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT (user_id, auth_provider, auth_uid, email, role, lawyer_status, is_provisioned, created_at, env)
  VALUES (source.user_id, source.auth_provider, source.auth_uid, source.email, source.role, source.lawyer_status, source.is_provisioned, CURRENT_TIMESTAMP(), source.env);
*/


-- ============================================
-- TABLE: user_profiles
-- Extended user profile information
-- ============================================
CREATE TABLE IF NOT EXISTS `legalai.user_profiles` (
  user_id STRING NOT NULL,                    -- FK to identity_users.user_id
  display_name STRING,                        -- Display name
  username STRING,                            -- Unique username handle
  avatar_url STRING,                          -- Avatar image URL (GCS)
  phone STRING,                               -- Phone number
  address_line_1 STRING,                      -- Street address
  address_line_2 STRING,                      -- Apartment, suite, etc.
  city STRING,                                -- City
  province_state STRING,                      -- Province or State
  postal_zip STRING,                          -- Postal or ZIP code
  country STRING,                             -- Country
  preferences_json STRING,                    -- JSON: theme, font_size, response_style, legal_tone
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = 'Extended user profile with personalization settings'
);

-- Upsert for user_profiles
/*
MERGE `legalai.user_profiles` AS target
USING (
  SELECT 
    @user_id AS user_id,
    @display_name AS display_name,
    @username AS username,
    @avatar_url AS avatar_url,
    @phone AS phone,
    @address_line_1 AS address_line_1,
    @address_line_2 AS address_line_2,
    @city AS city,
    @province_state AS province_state,
    @postal_zip AS postal_zip,
    @country AS country,
    @preferences_json AS preferences_json
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
    updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT (user_id, display_name, username, avatar_url, phone, address_line_1, address_line_2, city, province_state, postal_zip, country, preferences_json, updated_at)
  VALUES (source.user_id, source.display_name, source.username, source.avatar_url, source.phone, source.address_line_1, source.address_line_2, source.city, source.province_state, source.postal_zip, source.country, source.preferences_json, CURRENT_TIMESTAMP());
*/


-- ============================================
-- TABLE: user_consent
-- Cookie and data usage consent
-- ============================================
CREATE TABLE IF NOT EXISTS `legalai.user_consent` (
  user_id STRING NOT NULL,                    -- FK to identity_users.user_id
  necessary BOOL DEFAULT TRUE,                -- Always true (required)
  analytics BOOL DEFAULT FALSE,               -- Analytics cookies consent
  marketing BOOL DEFAULT FALSE,               -- Marketing cookies consent
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = 'User consent preferences for cookies and data usage'
);


-- ============================================
-- TABLE: access_requests
-- Access requests from non-provisioned users
-- ============================================
CREATE TABLE IF NOT EXISTS `legalai.access_requests` (
  id STRING NOT NULL,                         -- Request UUID
  email STRING NOT NULL,                      -- Requester email
  name STRING NOT NULL,                       -- Requester name
  requested_role STRING NOT NULL,             -- client | lawyer
  reason STRING,                              -- Reason for access
  organization STRING,                        -- Organization/firm name
  status STRING DEFAULT 'pending',            -- pending | approved | rejected
  reviewer_notes STRING,                      -- Admin notes
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  reviewed_at TIMESTAMP
)
OPTIONS (
  description = 'Access requests from users not yet provisioned'
);


-- ============================================
-- TABLE: lawyer_applications
-- Lawyer verification applications
-- ============================================
CREATE TABLE IF NOT EXISTS `legalai.lawyer_applications` (
  id STRING NOT NULL,                         -- Application UUID
  user_id STRING NOT NULL,                    -- FK to identity_users.user_id
  full_name STRING NOT NULL,                  -- Full legal name
  jurisdiction STRING NOT NULL,               -- Canada/USA + province/state
  bar_number STRING,                          -- Bar council or state bar number
  regulator_name STRING,                      -- e.g., Law Society of Ontario
  practice_areas STRING,                      -- Array as JSON string
  years_of_experience INT64,                  -- Years practicing
  firm_name STRING,                           -- Law firm name (optional)
  website_link STRING,                        -- Website URL (optional)
  bar_license_file_url STRING,                -- GCS URL for bar license
  government_id_file_url STRING,              -- GCS URL for government ID
  additional_credentials_file_url STRING,     -- GCS URL for additional docs
  status STRING DEFAULT 'pending',            -- pending | approved | rejected
  reviewer_notes STRING,                      -- Admin review notes
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  reviewed_at TIMESTAMP
)
OPTIONS (
  description = 'Lawyer verification applications with document uploads'
);


-- ============================================
-- TABLE: conversations
-- Chat conversations (scoped by user_id)
-- ============================================
CREATE TABLE IF NOT EXISTS `legalai.conversations` (
  id STRING NOT NULL,                         -- Conversation UUID
  user_id STRING NOT NULL,                    -- FK to identity_users.user_id
  title STRING,                               -- Conversation title
  law_category STRING,                        -- Legal category
  jurisdiction STRING,                        -- Jurisdiction
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = 'Chat conversations scoped by user'
);


-- ============================================
-- TABLE: messages
-- Chat messages within conversations
-- ============================================
CREATE TABLE IF NOT EXISTS `legalai.messages` (
  id STRING NOT NULL,                         -- Message UUID
  conversation_id STRING NOT NULL,            -- FK to conversations.id
  role STRING NOT NULL,                       -- user | assistant | system
  content STRING NOT NULL,                    -- Message content
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  meta_data STRING                            -- JSON metadata (citations, confidence, etc.)
)
OPTIONS (
  description = 'Chat messages within conversations'
);


-- ============================================
-- TABLE: attachments
-- File attachments in conversations
-- ============================================
CREATE TABLE IF NOT EXISTS `legalai.attachments` (
  id STRING NOT NULL,                         -- Attachment UUID
  conversation_id STRING NOT NULL,            -- FK to conversations.id
  filename STRING NOT NULL,                   -- Original filename
  file_type STRING,                           -- MIME type
  file_size INT64,                            -- Size in bytes
  storage_path STRING NOT NULL,               -- GCS path
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  meta_data STRING                            -- JSON metadata
)
OPTIONS (
  description = 'File attachments in conversations'
);


-- ============================================
-- TABLE: activity_events
-- Audit log for user actions
-- ============================================
CREATE TABLE IF NOT EXISTS `legalai.activity_events` (
  id STRING NOT NULL,                         -- Event UUID
  user_id STRING NOT NULL,                    -- FK to identity_users.user_id
  event_type STRING NOT NULL,                 -- login | logout | chat | document_generate | etc.
  event_data STRING,                          -- JSON event details
  ip_address STRING,                          -- Client IP
  user_agent STRING,                          -- Browser user agent
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = 'Audit log for user activity tracking'
);


-- ============================================
-- INDEXES (BigQuery uses clustering/partitioning instead)
-- ============================================

-- For identity_users: cluster by auth_provider, email
-- For user_profiles: cluster by user_id
-- For conversations: partition by DATE(created_at), cluster by user_id
-- For messages: partition by DATE(created_at), cluster by conversation_id
-- For activity_events: partition by DATE(created_at), cluster by user_id, event_type


-- ============================================
-- SAMPLE QUERIES
-- ============================================

-- Get user with profile
/*
SELECT 
  u.user_id,
  u.email,
  u.role,
  u.lawyer_status,
  u.is_provisioned,
  p.display_name,
  p.username,
  p.avatar_url,
  p.preferences_json
FROM `legalai.identity_users` u
LEFT JOIN `legalai.user_profiles` p ON u.user_id = p.user_id
WHERE u.email = @email;
*/

-- Get user's conversations with message count
/*
SELECT 
  c.id,
  c.title,
  c.law_category,
  c.created_at,
  COUNT(m.id) as message_count
FROM `legalai.conversations` c
LEFT JOIN `legalai.messages` m ON c.id = m.conversation_id
WHERE c.user_id = @user_id
GROUP BY c.id, c.title, c.law_category, c.created_at
ORDER BY c.updated_at DESC;
*/

-- Check if username is available
/*
SELECT COUNT(*) as count
FROM `legalai.user_profiles`
WHERE username = @username AND user_id != @current_user_id;
*/
