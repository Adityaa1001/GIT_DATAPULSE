-- DataPulse MySQL setup script.
-- Run this once against your MySQL server (as root or an admin user)
-- before starting the app. In MySQL Workbench, or via terminal:
--   mysql -u root -p < setup_database.sql

CREATE DATABASE IF NOT EXISTS datapulse;

-- Change the password below to something of your own, and make sure
-- your .env file (copied from .env.example) uses the same one.
CREATE USER IF NOT EXISTS 'datapulse_app'@'localhost' IDENTIFIED BY 'change_this_password';
GRANT ALL PRIVILEGES ON datapulse.* TO 'datapulse_app'@'localhost';
FLUSH PRIVILEGES;

-- Tables are created automatically by the app on first run
-- (see modules/db.py -> init_db()), so nothing further is needed here.