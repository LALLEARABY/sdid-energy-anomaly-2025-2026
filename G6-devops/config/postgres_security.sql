-- ==========================================
-- G6 - Postgres basic hardening (template)
-- ==========================================

-- NOTE:
-- Run at init time. Use POSTGRES_DB/USER in env.
-- You can customize for your schema later.

-- Reduce public permissions (safe default)
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE sdid_db FROM PUBLIC;

-- Ensure our app user has access (owner already has)
GRANT CONNECT ON DATABASE sdid_db TO sdid_user;
GRANT USAGE ON SCHEMA public TO sdid_user;

-- If you create tables with migrations, owner will be sdid_user
-- Otherwise, you can add explicit grants for read/write roles later.
