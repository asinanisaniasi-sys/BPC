# ============================================
# BLACK PRO CYBER BOT - Database Handler
# ============================================

import sqlite3
import asyncio
from datetime import datetime
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        referred_by INTEGER DEFAULT NULL,
        refer_count INTEGER DEFAULT 0,
        total_refers INTEGER DEFAULT 0,
        apk_claimed INTEGER DEFAULT 0,
        course_claimed INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        joined_at TEXT,
        last_active TEXT
    )''')

    # Referrals Table (tracks who referred whom - anti-fake)
    c.execute('''CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        referred_id INTEGER,
        referred_at TEXT,
        is_valid INTEGER DEFAULT 1
    )''')

    # APKs Table
    c.execute('''CREATE TABLE IF NOT EXISTS apks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        file_id TEXT,
        download_link TEXT,
        added_by INTEGER,
        added_at TEXT,
        is_active INTEGER DEFAULT 1
    )''')

    # Courses Table
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        file_id TEXT,
        download_link TEXT,
        added_by INTEGER,
        added_at TEXT,
        is_active INTEGER DEFAULT 1
    )''')

    # APK Claims Table
    c.execute('''CREATE TABLE IF NOT EXISTS apk_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        apk_id INTEGER,
        claimed_at TEXT
    )''')

    # Course Claims Table
    c.execute('''CREATE TABLE IF NOT EXISTS course_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        course_id INTEGER,
        claimed_at TEXT
    )''')

    # Admins Table
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY,
        added_by INTEGER,
        added_at TEXT
    )''')

    # Settings Table
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    # Insert default settings
    c.execute("INSERT OR IGNORE INTO settings VALUES ('apk_refer_required', '3')")
    c.execute("INSERT OR IGNORE INTO settings VALUES ('course_refer_required', '5')")

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


# ─── User Functions ───────────────────────────────────────

def add_user(user_id, username, full_name, referred_by=None):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''INSERT OR IGNORE INTO users 
                 (user_id, username, full_name, referred_by, joined_at, last_active)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (user_id, username, full_name, referred_by, now, now))
    conn.commit()
    inserted = c.rowcount > 0
    conn.close()
    return inserted


def get_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def update_last_active(user_id):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (now, user_id))
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned = 0")
    rows = c.fetchall()
    conn.close()
    return [r["user_id"] for r in rows]


def get_user_count():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM users")
    row = c.fetchone()
    conn.close()
    return row["cnt"]


def ban_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def unban_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def is_banned(user_id):
    user = get_user(user_id)
    return user and user["is_banned"] == 1


def update_username(user_id, username, full_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET username = ?, full_name = ? WHERE user_id = ?",
              (username, full_name, user_id))
    conn.commit()
    conn.close()


# ─── Referral Functions ──────────────────────────────────

def add_referral(referrer_id, referred_id):
    """Add referral and increment referrer's count. Returns True if success."""
    conn = get_connection()
    c = conn.cursor()

    # Check if this pair already exists
    c.execute("SELECT id FROM referrals WHERE referrer_id = ? AND referred_id = ?",
              (referrer_id, referred_id))
    if c.fetchone():
        conn.close()
        return False

    # Add referral
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO referrals (referrer_id, referred_id, referred_at) VALUES (?, ?, ?)",
              (referrer_id, referred_id, now))

    # Increment referrer's refer_count and total_refers
    c.execute("UPDATE users SET refer_count = refer_count + 1, total_refers = total_refers + 1 WHERE user_id = ?",
              (referrer_id,))
    conn.commit()
    conn.close()
    return True


def get_refer_count(user_id):
    user = get_user(user_id)
    return user["refer_count"] if user else 0


def reset_refer_count(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET refer_count = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_referral_list(referrer_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT r.referred_id, u.full_name, u.username, r.referred_at 
                 FROM referrals r JOIN users u ON r.referred_id = u.user_id
                 WHERE r.referrer_id = ? ORDER BY r.referred_at DESC LIMIT 10''',
              (referrer_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── APK Functions ───────────────────────────────────────

def add_apk(name, description, file_id, download_link, added_by):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''INSERT INTO apks (name, description, file_id, download_link, added_by, added_at)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (name, description, file_id, download_link, added_by, now))
    conn.commit()
    apk_id = c.lastrowid
    conn.close()
    return apk_id


def get_all_apks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM apks WHERE is_active = 1 ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_apk(apk_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM apks WHERE id = ? AND is_active = 1", (apk_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_apk(apk_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE apks SET is_active = 0 WHERE id = ?", (apk_id,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0


def claim_apk(user_id, apk_id):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO apk_claims (user_id, apk_id, claimed_at) VALUES (?, ?, ?)",
              (user_id, apk_id, now))
    c.execute("UPDATE users SET apk_claimed = apk_claimed + 1, refer_count = 0 WHERE user_id = ?",
              (user_id,))
    conn.commit()
    conn.close()


# ─── Course Functions ─────────────────────────────────────

def add_course(name, description, file_id, download_link, added_by):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''INSERT INTO courses (name, description, file_id, download_link, added_by, added_at)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (name, description, file_id, download_link, added_by, now))
    conn.commit()
    course_id = c.lastrowid
    conn.close()
    return course_id


def get_all_courses():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM courses WHERE is_active = 1 ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_course(course_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM courses WHERE id = ? AND is_active = 1", (course_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_course(course_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE courses SET is_active = 0 WHERE id = ?", (course_id,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0


def claim_course(user_id, course_id):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO course_claims (user_id, course_id, claimed_at) VALUES (?, ?, ?)",
              (user_id, course_id, now))
    c.execute("UPDATE users SET course_claimed = course_claimed + 1, refer_count = 0 WHERE user_id = ?",
              (user_id,))
    conn.commit()
    conn.close()


# ─── Admin Functions ──────────────────────────────────────

def add_admin(user_id, added_by):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT OR IGNORE INTO admins (user_id, added_by, added_at) VALUES (?, ?, ?)",
              (user_id, added_by, now))
    conn.commit()
    inserted = c.rowcount > 0
    conn.close()
    return inserted


def remove_admin(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0


def get_db_admins():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM admins")
    rows = c.fetchall()
    conn.close()
    return [r["user_id"] for r in rows]


# ─── Settings Functions ───────────────────────────────────

def get_setting(key):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row["value"] if row else None


def set_setting(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()
