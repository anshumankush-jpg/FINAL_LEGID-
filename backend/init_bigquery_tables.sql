-- BigQuery Table Creation Script
-- Project: auth-login-page-481522
-- Dataset: legalai

-- ============================================
-- 1. IDENTITY USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS `auth-login-page-481522.legalai.identity_users` (
  user_id STRING NOT NULL,
  auth_provider STRING NOT NULL,  -- google, microsoft, email
  auth_uid STRING NOT NULL,        -- Provider's user ID
  email STRING NOT NULL,
  display_name STRING,
  photo_url STRING,
  role STRING NOT NULL,            -- customer, lawyer, admin
  lawyer_status STRING,            -- not_applicable, pending, approved, rejected
  is_active BOOL,
  is_verified BOOL,
  created_at TIMESTAMP NOT NULL,
  last_login_at TIMESTAMP,
  updated_at TIMESTAMP NOT NULL,
  env STRING NOT NULL  -- dev, staging, prod
)
PARTITION BY DATE(created_at)
OPTIONS(
  description="User identity records with managed IDs",
  labels=[("app", "legid"), ("type", "identity")]
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_auth_uid 
ON `auth-login-page-481522.legalai.identity_users`(auth_uid, auth_provider);

CREATE INDEX IF NOT EXISTS idx_email 
ON `auth-login-page-481522.legalai.identity_users`(email);


-- ============================================
-- 2. LOGIN EVENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS `auth-login-page-481522.legalai.login_events` (
  event_id STRING NOT NULL,
  user_id STRING NOT NULL,
  auth_provider STRING NOT NULL,  -- google, microsoft, email
  event_type STRING NOT NULL,      -- login, logout, login_failed
  ip_address STRING,
  user_agent STRING,
  success BOOL NOT NULL,
  failure_reason STRING,
  timestamp TIMESTAMP NOT NULL,
  env STRING NOT NULL  -- dev, staging, prod
)
PARTITION BY DATE(timestamp)
OPTIONS(
  description="Login and authentication event audit trail",
  labels=[("app", "legid"), ("type", "audit")]
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_events 
ON `auth-login-page-481522.legalai.login_events`(user_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_event_type 
ON `auth-login-page-481522.legalai.login_events`(event_type, timestamp DESC);


-- ============================================
-- 3. LAWYER APPLICATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS `auth-login-page-481522.legalai.lawyer_applications` (
  application_id STRING NOT NULL,
  user_id STRING NOT NULL,
  full_name STRING NOT NULL,
  email STRING NOT NULL,
  phone_number STRING,
  country STRING NOT NULL,
  jurisdiction STRING NOT NULL,
  bar_number STRING NOT NULL,
  regulator_name STRING NOT NULL,
  bar_admission_date DATE,
  practice_areas ARRAY<STRING>,
  years_of_experience INT64,
  firm_name STRING,
  firm_address STRING,
  website_url STRING,
  bar_license_url STRING NOT NULL,
  government_id_url STRING,
  credentials_url STRING,
  status STRING NOT NULL,  -- pending, approved, rejected
  submitted_at TIMESTAMP NOT NULL,
  reviewed_at TIMESTAMP,
  reviewed_by STRING,
  rejection_reason STRING,
  env STRING NOT NULL  -- dev, staging, prod
)
PARTITION BY DATE(submitted_at)
OPTIONS(
  description="Lawyer verification applications",
  labels=[("app", "legid"), ("type", "application")]
);


-- ============================================
-- 4. CONVERSATION HISTORY TABLE (Optional)
-- ============================================
CREATE TABLE IF NOT EXISTS `auth-login-page-481522.legalai.conversations` (
  conversation_id STRING NOT NULL,
  user_id STRING NOT NULL,
  title STRING,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  message_count INT64,
  preview STRING,
  is_archived BOOL,
  env STRING NOT NULL  -- dev, staging, prod
)
PARTITION BY DATE(created_at)
OPTIONS(
  description="User conversation history",
  labels=[("app", "legid"), ("type", "chat")]
);


-- ============================================
-- 5. MESSAGES TABLE (Optional)
-- ============================================
CREATE TABLE IF NOT EXISTS `auth-login-page-481522.legalai.messages` (
  message_id STRING NOT NULL,
  conversation_id STRING NOT NULL,
  user_id STRING NOT NULL,
  role STRING NOT NULL,  -- user, assistant, system
  content STRING NOT NULL,
  attachments JSON,
  metadata JSON,
  created_at TIMESTAMP NOT NULL,
  env STRING NOT NULL  -- dev, staging, prod
)
PARTITION BY DATE(created_at)
OPTIONS(
  description="Chat messages",
  labels=[("app", "legid"), ("type", "chat")]
);


-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- Active users in last 30 days
CREATE OR REPLACE VIEW `auth-login-page-481522.legalai.active_users_30d` AS
SELECT 
  COUNT(DISTINCT user_id) as active_users,
  auth_provider,
  env
FROM `auth-login-page-481522.legalai.login_events`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND success = TRUE
GROUP BY auth_provider, env;

-- Login success rate
CREATE OR REPLACE VIEW `auth-login-page-481522.legalai.login_success_rate` AS
SELECT 
  auth_provider,
  env,
  COUNTIF(success = TRUE) as successful_logins,
  COUNTIF(success = FALSE) as failed_logins,
  ROUND(COUNTIF(success = TRUE) / COUNT(*) * 100, 2) as success_rate_percent
FROM `auth-login-page-481522.legalai.login_events`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY auth_provider, env;
