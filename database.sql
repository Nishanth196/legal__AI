-- ══════════════════════════════════════════════════════════════════
-- LexReg AI – Full Database Schema + Seed Data
-- MySQL 8.0+
-- ══════════════════════════════════════════════════════════════════

CREATE DATABASE IF NOT EXISTS lexreg_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lexreg_db;

-- ── Users ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(120)   NOT NULL,
  email         VARCHAR(150)   NOT NULL UNIQUE,
  password_hash VARCHAR(255)   NOT NULL DEFAULT '',
  role          ENUM('user','admin') NOT NULL DEFAULT 'user',
  is_verified   TINYINT(1)     NOT NULL DEFAULT 0,
  avatar        VARCHAR(255)   DEFAULT '',
  created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_login    DATETIME       NULL,
  INDEX idx_email (email)
) ENGINE=InnoDB;

-- ── Company Profile ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS company_profile (
  id                   INT AUTO_INCREMENT PRIMARY KEY,
  user_id              INT          NOT NULL UNIQUE,
  company_name         VARCHAR(200) NOT NULL,
  business_type        VARCHAR(100),
  owner_name           VARCHAR(120),
  designation          VARCHAR(100),
  email                VARCHAR(150),
  phone                VARCHAR(20),
  website              VARCHAR(200),
  address              TEXT,
  pan_number           VARCHAR(20),
  gst_number           VARCHAR(20),
  cin_number           VARCHAR(30),
  registration_date    VARCHAR(20),
  authorized_signatory VARCHAR(120),
  logo_path            VARCHAR(255),
  seal_path            VARCHAR(255),
  updated_at           DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ── Document Templates ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS document_templates (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(200) NOT NULL,
  category    VARCHAR(100),
  slug        VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  icon        VARCHAR(50)  DEFAULT 'fa-file-alt',
  is_active   TINYINT(1)   NOT NULL DEFAULT 1,
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ── Generated Documents ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS generated_documents (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT          NOT NULL,
  template_id INT          NULL,
  title       VARCHAR(300) NOT NULL,
  content     LONGTEXT,
  status      ENUM('draft','generated','completed') NOT NULL DEFAULT 'draft',
  pdf_path    VARCHAR(255),
  docx_path   VARCHAR(255),
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (template_id) REFERENCES document_templates(id) ON DELETE SET NULL,
  INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB;

-- ── Notifications ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT          NOT NULL,
  message    VARCHAR(500) NOT NULL,
  type       ENUM('success','info','warning','error') DEFAULT 'info',
  is_read    TINYINT(1)   NOT NULL DEFAULT 0,
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_read (user_id, is_read)
) ENGINE=InnoDB;

-- ── Activity Logs ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS activity_logs (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT          NOT NULL,
  action     VARCHAR(100) NOT NULL,
  details    TEXT,
  ip_address VARCHAR(45),
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_time (user_id, created_at)
) ENGINE=InnoDB;

-- ── Chat History ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chat_history (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT  NOT NULL,
  message    TEXT NOT NULL,
  response   TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ── Analytics ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analytics (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  date        DATE    NOT NULL UNIQUE,
  total_users INT     NOT NULL DEFAULT 0,
  total_docs  INT     NOT NULL DEFAULT 0,
  api_calls   INT     NOT NULL DEFAULT 0,
  downloads   INT     NOT NULL DEFAULT 0
) ENGINE=InnoDB;

-- ── Downloads ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS downloads (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT  NOT NULL,
  document_id   INT  NOT NULL,
  format        ENUM('pdf','docx') NOT NULL,
  downloaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (document_id) REFERENCES generated_documents(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ── Settings ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS settings (
  id      INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT          NOT NULL,
  `key`   VARCHAR(100) NOT NULL,
  value   TEXT,
  UNIQUE KEY uq_user_setting (user_id, `key`),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ══════════════════════════════════════════════════════════════════
-- SEED DATA
-- ══════════════════════════════════════════════════════════════════

-- Demo Users (passwords: Demo@123 and Admin@123 – bcrypt hashed)
INSERT IGNORE INTO users (id, name, email, password_hash, role, is_verified, created_at) VALUES
(1, 'Admin',      'admin@lexregai.com',            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhcanFp8.qhH9kIlRvqNqO', 'admin', 1, NOW()),
(2, 'Nishanth S', 'nishanth@novaspheretech.com',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhcanFp8.qhH9kIlRvqNqO', 'user',  1, NOW());

-- Demo Company Profile
INSERT IGNORE INTO company_profile
  (user_id, company_name, business_type, owner_name, designation, email, phone,
   website, address, pan_number, gst_number, cin_number, registration_date, authorized_signatory)
VALUES
  (2, 'NovaSphere Technologies Private Limited', 'Software & IT Services',
   'Nishanth S', 'Managing Director', 'support@novaspheretech.com', '+91 9876543210',
   'www.novaspheretech.com',
   'No.18, Innovation Park, Coimbatore, Tamil Nadu, India – 641021',
   'ABCDE1234F', '33ABCDE1234F1Z5', 'U72900TZ2025PTC123456',
   '15-04-2025', 'Nishanth S');

-- Document Templates (20 templates)
INSERT IGNORE INTO document_templates (name, category, slug, is_active) VALUES
('GST Registration',           'compliance',  'gst_registration',    1),
('Business License',           'license',     'business_license',    1),
('Trade License',              'license',     'trade_license',       1),
('Import Export License',      'license',     'ie_license',          1),
('Company Registration',       'corporate',   'company_registration',1),
('Partnership Agreement',      'agreement',   'partnership_agreement',1),
('Non Disclosure Agreement',   'agreement',   'nda',                 1),
('Privacy Policy',             'policy',      'privacy_policy',      1),
('Terms and Conditions',       'policy',      'terms_conditions',    1),
('Employee Agreement',         'hr',          'employee_agreement',  1),
('Offer Letter',               'hr',          'offer_letter',        1),
('Vendor Agreement',           'agreement',   'vendor_agreement',    1),
('Compliance Report',          'compliance',  'compliance_report',   1),
('Regulatory Submission',      'regulatory',  'regulatory_submission',1),
('Tax Declaration',            'tax',         'tax_declaration',     1),
('Environmental Clearance',    'regulatory',  'env_clearance',       1),
('Factory License',            'license',     'factory_license',     1),
('ISO Compliance',             'compliance',  'iso_compliance',      1),
('MSME Registration',          'corporate',   'msme_registration',   1),
('Startup India Registration', 'corporate',   'startup_india',       1);

-- Sample Notifications for demo user
INSERT IGNORE INTO notifications (user_id, message, type, is_read) VALUES
(2, 'Welcome to LexReg AI! Your account is ready.', 'success', 0),
(2, 'Complete your company profile for better document generation.', 'info', 0),
(2, 'New template available: Startup India Registration', 'info', 0);

-- Sample Activity for demo user  
INSERT IGNORE INTO activity_logs (user_id, action, details) VALUES
(2, 'LOGIN',    'Demo account login'),
(2, 'REGISTER', 'Account created');

-- Analytics seed
INSERT IGNORE INTO analytics (date, total_users, total_docs, api_calls, downloads)
VALUES (CURDATE(), 2, 0, 0, 0);

-- ── Machine Learning Logs ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS model_training_logs (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  dataset_name  VARCHAR(255) NOT NULL,
  accuracy      FLOAT,
  precision_val FLOAT,
  recall        FLOAT,
  f1_score      FLOAT,
  training_time FLOAT,
  trained_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  status        VARCHAR(50) DEFAULT 'Success'
) ENGINE=InnoDB;
