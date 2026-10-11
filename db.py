"""
DataPulse MySQL data-access layer.

Reads connection settings from a .env file (see .env.example). Every
public function fails soft: if MySQL isn't reachable, functions return
None/False/[] instead of raising, and the last error is stashed in
`last_error` so calling code can show a status message. This means the
Streamlit app keeps working on session state alone if the DB is down —
important for a live demo where MySQL might not be running.
"""

import os

import bcrypt
import mysql.connector
from mysql.connector import Error as MySQLError
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "datapulse_app"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "datapulse"),
    "connection_timeout": 4,
}

last_error: str = ""


def _connect():
    global last_error
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        last_error = ""
        return conn
    except MySQLError as e:
        last_error = str(e)
        return None


def is_available() -> bool:
    """Quick connectivity check. Cheap enough to call once per page render."""
    conn = _connect()
    if conn is None:
        return False
    conn.close()
    return True


def init_db() -> bool:
    """Creates the schema if it doesn't exist yet. Safe to call every
    startup — CREATE TABLE IF NOT EXISTS is idempotent."""
    conn = _connect()
    if conn is None:
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NULL,
                filename VARCHAR(255) NOT NULL,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                row_count INT DEFAULT 0,
                column_count INT DEFAULT 0,
                missing_pct FLOAT DEFAULT 0,
                duplicate_pct FLOAT DEFAULT 0,
                status VARCHAR(50) DEFAULT 'needs_review',
                dq_score INT DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB;
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                upload_id INT NULL,
                filename VARCHAR(255) NOT NULL,
                action_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                action VARCHAR(20) NOT NULL,
                column_name VARCHAR(255),
                issue_type VARCHAR(50),
                description TEXT,
                fix_applied TEXT,
                FOREIGN KEY (upload_id) REFERENCES uploads(id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        """)
        conn.commit()
        cur.close()
        return True
    except MySQLError as e:
        global last_error
        last_error = str(e)
        return False
    finally:
        conn.close()


# ============================================================
# Users
# ============================================================
def create_user(email: str, password: str):
    """Returns (True, 'message') on success, (False, 'message') on failure."""
    conn = _connect()
    if conn is None:
        return False, f"Database unavailable: {last_error}"
    try:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
            (email, password_hash),
        )
        conn.commit()
        cur.close()
        return True, "Account created."
    except MySQLError as e:
        if e.errno == 1062:  # duplicate key
            return False, "An account with that email already exists."
        return False, f"Could not create account: {e}"
    finally:
        conn.close()


def verify_user(email: str, password: str):
    """Returns the user dict (without password_hash) on success, None on
    failure (wrong password, no such user, or DB unavailable)."""
    conn = _connect()
    if conn is None:
        return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            user.pop("password_hash", None)
            return user
        return None
    except MySQLError as e:
        global last_error
        last_error = str(e)
        return None
    finally:
        conn.close()


# ============================================================
# Uploads
# ============================================================
def insert_upload(filename, user_id=None, row_count=0, column_count=0,
                   missing_pct=0.0, duplicate_pct=0.0, status="needs_review", dq_score=0):
    """Returns the new upload's id, or None on failure."""
    conn = _connect()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO uploads
               (user_id, filename, row_count, column_count, missing_pct, duplicate_pct, status, dq_score)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (user_id, filename, row_count, column_count, missing_pct, duplicate_pct, status, dq_score),
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        return new_id
    except MySQLError as e:
        global last_error
        last_error = str(e)
        return None
    finally:
        conn.close()


def get_uploads(user_id=None):
    """Returns a list of upload dicts, most recent first. Empty list on
    failure or if there are none yet."""
    conn = _connect()
    if conn is None:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        if user_id:
            cur.execute("SELECT * FROM uploads WHERE user_id=%s ORDER BY uploaded_at DESC", (user_id,))
        else:
            cur.execute("SELECT * FROM uploads ORDER BY uploaded_at DESC")
        rows = cur.fetchall()
        cur.close()
        return rows
    except MySQLError as e:
        global last_error
        last_error = str(e)
        return []
    finally:
        conn.close()


# ============================================================
# Audit log
# ============================================================
def insert_audit_log(filename, action, column_name, issue_type, description, fix_applied, upload_id=None):
    conn = _connect()
    if conn is None:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO audit_log
               (upload_id, filename, action, column_name, issue_type, description, fix_applied)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (upload_id, filename, action, column_name, issue_type, description, fix_applied),
        )
        conn.commit()
        cur.close()
        return True
    except MySQLError as e:
        global last_error
        last_error = str(e)
        return False
    finally:
        conn.close()


def get_audit_log(filename=None):
    conn = _connect()
    if conn is None:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        if filename:
            cur.execute("SELECT * FROM audit_log WHERE filename=%s ORDER BY action_time DESC", (filename,))
        else:
            cur.execute("SELECT * FROM audit_log ORDER BY action_time DESC")
        rows = cur.fetchall()
        cur.close()
        return rows
    except MySQLError as e:
        global last_error
        last_error = str(e)
        return []
    finally:
        conn.close()