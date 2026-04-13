from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from emailer import email_configured, send_email_message

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
DB_PATH = DATA_DIR / "pethelpai.db"


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                timezone TEXT DEFAULT 'America/New_York',
                role TEXT DEFAULT 'user',
                notification_email INTEGER DEFAULT 1,
                notification_in_app INTEGER DEFAULT 1,
                notification_push INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                provider TEXT DEFAULT 'manual',
                plan TEXT DEFAULT 'free',
                status TEXT DEFAULT 'free',
                started_at TEXT,
                expires_at TEXT,
                renewal_at TEXT,
                trial_ends_at TEXT,
                auto_renew INTEGER DEFAULT 1,
                external_subscription_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                breed TEXT,
                birth_date TEXT,
                age_text TEXT,
                sex TEXT,
                weight REAL,
                sterilized INTEGER DEFAULT 0,
                color TEXT,
                allergies TEXT,
                chronic_conditions TEXT,
                chip_number TEXT,
                avatar_url TEXT,
                clinic_name TEXT,
                vet_name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS care_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                scheduled_at TEXT NOT NULL,
                recurrence_rule TEXT DEFAULT 'none',
                reminder_settings TEXT DEFAULT '[]',
                status TEXT DEFAULT 'planned',
                completed_at TEXT,
                parent_event_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_event_id) REFERENCES care_events(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS health_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                log_type TEXT NOT NULL,
                symptom TEXT,
                severity TEXT,
                description TEXT,
                attachment_url TEXT,
                recorded_at TEXT NOT NULL,
                appetite TEXT,
                activity TEXT,
                stool_vomit TEXT,
                mood TEXT,
                related_event_id INTEGER,
                related_medication_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS medication_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                medicine_name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                note TEXT,
                status TEXT DEFAULT 'active',
                last_given_at TEXT,
                next_due_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS weight_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                weight REAL NOT NULL,
                measured_at TEXT NOT NULL,
                note TEXT,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                spent_at TEXT NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                file_url TEXT NOT NULL,
                file_name TEXT NOT NULL,
                uploaded_at TEXT NOT NULL,
                note TEXT,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pet_id INTEGER,
                event_id INTEGER,
                channel TEXT NOT NULL,
                send_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
                FOREIGN KEY (event_id) REFERENCES care_events(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS product_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_name TEXT NOT NULL,
                meta TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )


def log_product_event(user_id: int | None, event_name: str, meta: dict[str, Any] | None = None) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO product_events (user_id, event_name, meta, created_at) VALUES (?, ?, ?, ?)",
            (user_id, event_name, json.dumps(meta or {}, ensure_ascii=False), now_iso()),
        )


def hash_password(password: str, salt: str | None = None) -> str:
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.sha256(f"{salt_value}:{password}".encode("utf-8")).hexdigest()
    return f"{salt_value}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    if "$" not in stored_hash:
        return False
    salt, existing = stored_hash.split("$", 1)
    candidate = hash_password(password, salt).split("$", 1)[1]
    return secrets.compare_digest(candidate, existing)


def user_count() -> int:
    with connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
    return int(row["count"])


def create_user(name: str, email: str, password: str, timezone: str) -> dict[str, Any]:
    created_at = now_iso()
    normalized_email = email.strip().lower()
    role = "admin" if user_count() == 0 else "user"
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash, timezone, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name.strip(), normalized_email, hash_password(password), timezone, role, created_at, created_at),
        )
        user_id = int(cursor.lastrowid)
        conn.execute(
            """
            INSERT INTO subscriptions (user_id, provider, plan, status, created_at, updated_at)
            VALUES (?, 'manual', 'free', 'free', ?, ?)
            """,
            (user_id, created_at, created_at),
        )
    log_product_event(user_id, "registration_completed")
    return get_user(user_id) or {}


def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
    user = to_dict(row)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    log_product_event(int(user["id"]), "login")
    return user


def update_password(email: str, new_password: str) -> bool:
    with connect() as conn:
        cursor = conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE email = ?",
            (hash_password(new_password), now_iso(), email.strip().lower()),
        )
    return cursor.rowcount > 0


def get_user(user_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return to_dict(row)


def update_user_settings(
    user_id: int,
    *,
    name: str,
    timezone: str,
    notification_email: bool,
    notification_in_app: bool,
    notification_push: bool,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE users
            SET name = ?, timezone = ?, notification_email = ?, notification_in_app = ?, notification_push = ?, updated_at = ?
            WHERE id = ?
            """,
            (name.strip(), timezone, int(notification_email), int(notification_in_app), int(notification_push), now_iso(), user_id),
        )


def ensure_subscription(user_id: int) -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            timestamp = now_iso()
            conn.execute(
                """
                INSERT INTO subscriptions (user_id, provider, plan, status, created_at, updated_at)
                VALUES (?, 'manual', 'free', 'free', ?, ?)
                """,
                (user_id, timestamp, timestamp),
            )
    return get_subscription(user_id)


def refresh_subscription_state(user_id: int) -> None:
    subscription = get_subscription(user_id)
    now = datetime.utcnow()
    updates: dict[str, Any] = {}
    trial_end = parse_iso(subscription.get("trial_ends_at"))
    expires_at = parse_iso(subscription.get("expires_at"))
    status = subscription.get("status")
    if status == "trialing" and trial_end and trial_end <= now:
        updates = {"status": "free", "plan": "free", "trial_ends_at": None, "expires_at": None, "renewal_at": None}
    elif status == "canceled" and expires_at and expires_at <= now:
        updates = {"status": "free", "plan": "free", "expires_at": None, "renewal_at": None}
    if updates:
        set_subscription_state(user_id, **updates)


def get_subscription(user_id: int) -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,)).fetchone()
    subscription = to_dict(row) or {}
    if not subscription:
        return ensure_subscription(user_id)
    return subscription


def set_subscription_state(user_id: int, **updates: Any) -> None:
    if not updates:
        return
    updates["updated_at"] = now_iso()
    assignments = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [user_id]
    with connect() as conn:
        conn.execute(f"UPDATE subscriptions SET {assignments} WHERE user_id = ?", values)


def subscription_is_premium(subscription: dict[str, Any]) -> bool:
    return subscription.get("status") in {"trialing", "active"}


def start_trial(user_id: int) -> None:
    timestamp = datetime.utcnow().replace(microsecond=0)
    set_subscription_state(
        user_id,
        provider="manual",
        plan="premium_monthly",
        status="trialing",
        started_at=timestamp.isoformat(),
        trial_ends_at=(timestamp + timedelta(days=7)).isoformat(),
        renewal_at=(timestamp + timedelta(days=7)).isoformat(),
        expires_at=None,
    )
    log_product_event(user_id, "subscription_trial_started")


def activate_subscription(user_id: int, plan: str) -> None:
    timestamp = datetime.utcnow().replace(microsecond=0)
    renewal_at = timestamp + (timedelta(days=365) if plan == "premium_yearly" else timedelta(days=30))
    set_subscription_state(
        user_id,
        provider="manual",
        plan=plan,
        status="active",
        started_at=timestamp.isoformat(),
        renewal_at=renewal_at.isoformat(),
        expires_at=renewal_at.isoformat(),
        trial_ends_at=None,
    )
    log_product_event(user_id, "payment_success", {"plan": plan})


def cancel_subscription(user_id: int) -> None:
    subscription = get_subscription(user_id)
    expires_at = subscription.get("expires_at") or subscription.get("renewal_at") or now_iso()
    set_subscription_state(user_id, status="canceled", expires_at=expires_at, auto_renew=0)
    log_product_event(user_id, "subscription_canceled")


def free_limits(subscription: dict[str, Any]) -> dict[str, Any]:
    if subscription_is_premium(subscription):
        return {
            "max_pets": None,
            "max_events": None,
            "documents_enabled": True,
            "advanced_reminders": True,
            "family_access": True,
            "analytics_enabled": True,
        }
    return {
        "max_pets": 1,
        "max_events": 12,
        "documents_enabled": False,
        "advanced_reminders": False,
        "family_access": False,
        "analytics_enabled": False,
    }


def count_user_pets(user_id: int) -> int:
    with connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM pets WHERE user_id = ?", (user_id,)).fetchone()
    return int(row["count"])


def count_active_events(user_id: int) -> int:
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM care_events WHERE user_id = ? AND status = 'planned'",
            (user_id,),
        ).fetchone()
    return int(row["count"])


def create_pet(user_id: int, payload: dict[str, Any]) -> int:
    timestamp = now_iso()
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO pets (
                user_id, name, species, breed, birth_date, age_text, sex, weight, sterilized,
                color, allergies, chronic_conditions, chip_number, avatar_url, clinic_name, vet_name, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                payload["name"].strip(),
                payload["species"],
                payload.get("breed", "").strip(),
                payload.get("birth_date"),
                payload.get("age_text", "").strip(),
                payload.get("sex", ""),
                payload.get("weight"),
                int(bool(payload.get("sterilized"))),
                payload.get("color", "").strip(),
                payload.get("allergies", "").strip(),
                payload.get("chronic_conditions", "").strip(),
                payload.get("chip_number", "").strip(),
                payload.get("avatar_url"),
                payload.get("clinic_name", "").strip(),
                payload.get("vet_name", "").strip(),
                timestamp,
                timestamp,
            ),
        )
        pet_id = int(cursor.lastrowid)
    log_product_event(user_id, "pet_added", {"pet_id": pet_id, "species": payload["species"]})
    return pet_id


def update_pet(pet_id: int, user_id: int, payload: dict[str, Any]) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE pets
            SET name = ?, species = ?, breed = ?, birth_date = ?, age_text = ?, sex = ?, weight = ?, sterilized = ?,
                color = ?, allergies = ?, chronic_conditions = ?, chip_number = ?, avatar_url = ?, clinic_name = ?, vet_name = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                payload["name"].strip(),
                payload["species"],
                payload.get("breed", "").strip(),
                payload.get("birth_date"),
                payload.get("age_text", "").strip(),
                payload.get("sex", ""),
                payload.get("weight"),
                int(bool(payload.get("sterilized"))),
                payload.get("color", "").strip(),
                payload.get("allergies", "").strip(),
                payload.get("chronic_conditions", "").strip(),
                payload.get("chip_number", "").strip(),
                payload.get("avatar_url"),
                payload.get("clinic_name", "").strip(),
                payload.get("vet_name", "").strip(),
                now_iso(),
                pet_id,
                user_id,
            ),
        )


def list_pets(user_id: int) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM pets WHERE user_id = ? ORDER BY created_at ASC",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_pet(user_id: int, pet_id: int) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM pets WHERE id = ? AND user_id = ?", (pet_id, user_id)).fetchone()
    return to_dict(row)


def save_uploaded_file(uploaded_file: Any, user_id: int, prefix: str) -> str:
    extension = Path(uploaded_file.name).suffix.lower()
    safe_name = f"{prefix}_{user_id}_{uuid4().hex}{extension}"
    target = UPLOADS_DIR / safe_name
    target.write_bytes(uploaded_file.getbuffer())
    return str(target)


def _next_recurrence(scheduled_at: str, recurrence_rule: str) -> str | None:
    current = parse_iso(scheduled_at)
    if current is None or recurrence_rule == "none":
        return None
    if recurrence_rule == "daily":
        return (current + timedelta(days=1)).isoformat()
    if recurrence_rule == "weekly":
        return (current + timedelta(weeks=1)).isoformat()
    if recurrence_rule == "monthly":
        return (current + timedelta(days=30)).isoformat()
    if recurrence_rule == "yearly":
        return (current + timedelta(days=365)).isoformat()
    return None


def create_care_event(user_id: int, payload: dict[str, Any]) -> int:
    timestamp = now_iso()
    reminder_settings = json.dumps(payload.get("reminder_settings", []), ensure_ascii=False)
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO care_events (
                pet_id, user_id, type, title, description, scheduled_at, recurrence_rule, reminder_settings,
                status, completed_at, parent_event_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'planned', NULL, ?, ?, ?)
            """,
            (
                payload["pet_id"],
                user_id,
                payload["type"],
                payload["title"].strip(),
                payload.get("description", "").strip(),
                payload["scheduled_at"],
                payload.get("recurrence_rule", "none"),
                reminder_settings,
                payload.get("parent_event_id"),
                timestamp,
                timestamp,
            ),
        )
        event_id = int(cursor.lastrowid)
    log_product_event(user_id, "care_event_created", {"event_id": event_id, "type": payload["type"]})
    return event_id


def list_care_events(user_id: int, pet_id: int | None = None, status: str | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT care_events.*, pets.name AS pet_name
        FROM care_events
        JOIN pets ON pets.id = care_events.pet_id
        WHERE care_events.user_id = ?
    """
    params: list[Any] = [user_id]
    if pet_id:
        query += " AND care_events.pet_id = ?"
        params.append(pet_id)
    if status:
        query += " AND care_events.status = ?"
        params.append(status)
    query += " ORDER BY care_events.scheduled_at ASC"
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def list_upcoming_events(user_id: int, limit: int = 8) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT care_events.*, pets.name AS pet_name
            FROM care_events
            JOIN pets ON pets.id = care_events.pet_id
            WHERE care_events.user_id = ? AND care_events.status = 'planned'
            ORDER BY care_events.scheduled_at ASC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def list_today_tasks(user_id: int) -> list[dict[str, Any]]:
    now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end = now + timedelta(days=1)
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT care_events.*, pets.name AS pet_name
            FROM care_events
            JOIN pets ON pets.id = care_events.pet_id
            WHERE care_events.user_id = ? AND care_events.status = 'planned'
              AND care_events.scheduled_at >= ? AND care_events.scheduled_at < ?
            ORDER BY care_events.scheduled_at ASC
            """,
            (user_id, now.isoformat(), end.isoformat()),
        ).fetchall()
    return [dict(row) for row in rows]


def mark_event_completed(user_id: int, event_id: int) -> None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM care_events WHERE id = ? AND user_id = ?", (event_id, user_id)).fetchone()
        event = to_dict(row)
        if not event:
            return
        completed_at = now_iso()
        conn.execute(
            "UPDATE care_events SET status = 'completed', completed_at = ?, updated_at = ? WHERE id = ?",
            (completed_at, completed_at, event_id),
        )
        next_scheduled = _next_recurrence(event["scheduled_at"], event["recurrence_rule"])
        if next_scheduled:
            conn.execute(
                """
                INSERT INTO care_events (
                    pet_id, user_id, type, title, description, scheduled_at, recurrence_rule, reminder_settings,
                    status, parent_event_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'planned', ?, ?, ?)
                """,
                (
                    event["pet_id"],
                    event["user_id"],
                    event["type"],
                    event["title"],
                    event["description"],
                    next_scheduled,
                    event["recurrence_rule"],
                    event["reminder_settings"],
                    event["id"],
                    completed_at,
                    completed_at,
                ),
            )
    log_product_event(user_id, "care_event_completed", {"event_id": event_id})


def mark_event_missed(user_id: int, event_id: int) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE care_events SET status = 'missed', updated_at = ? WHERE id = ? AND user_id = ?",
            (now_iso(), event_id, user_id),
        )


def create_health_log(user_id: int, payload: dict[str, Any]) -> int:
    attachment_url = payload.get("attachment_url")
    recorded_at = payload.get("recorded_at") or now_iso()
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO health_logs (
                pet_id, user_id, log_type, symptom, severity, description, attachment_url, recorded_at,
                appetite, activity, stool_vomit, mood, related_event_id, related_medication_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["pet_id"],
                user_id,
                payload["log_type"],
                payload.get("symptom", "").strip(),
                payload.get("severity"),
                payload.get("description", "").strip(),
                attachment_url,
                recorded_at,
                payload.get("appetite", "").strip(),
                payload.get("activity", "").strip(),
                payload.get("stool_vomit", "").strip(),
                payload.get("mood", "").strip(),
                payload.get("related_event_id"),
                payload.get("related_medication_id"),
                now_iso(),
            ),
        )
        log_id = int(cursor.lastrowid)
    log_product_event(user_id, "health_log_added", {"log_id": log_id})
    return log_id


def list_health_logs(user_id: int, pet_id: int | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT health_logs.*, pets.name AS pet_name
        FROM health_logs
        JOIN pets ON pets.id = health_logs.pet_id
        WHERE health_logs.user_id = ?
    """
    params: list[Any] = [user_id]
    if pet_id:
        query += " AND health_logs.pet_id = ?"
        params.append(pet_id)
    query += " ORDER BY health_logs.recorded_at DESC"
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def _next_med_due(start_iso: str, frequency: str) -> str | None:
    base = parse_iso(start_iso)
    if base is None:
        return None
    if frequency == "once":
        return None
    if frequency == "every_12h":
        return (base + timedelta(hours=12)).isoformat()
    if frequency == "daily":
        return (base + timedelta(days=1)).isoformat()
    if frequency == "weekly":
        return (base + timedelta(weeks=1)).isoformat()
    if frequency == "monthly":
        return (base + timedelta(days=30)).isoformat()
    return None


def create_medication_course(user_id: int, payload: dict[str, Any]) -> int:
    timestamp = now_iso()
    next_due_at = _next_med_due(payload["start_date"], payload["frequency"]) or payload["start_date"]
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO medication_courses (
                pet_id, user_id, medicine_name, dosage, frequency, start_date, end_date,
                note, status, last_given_at, next_due_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', NULL, ?, ?, ?)
            """,
            (
                payload["pet_id"],
                user_id,
                payload["medicine_name"].strip(),
                payload.get("dosage", "").strip(),
                payload["frequency"],
                payload["start_date"],
                payload.get("end_date"),
                payload.get("note", "").strip(),
                next_due_at,
                timestamp,
                timestamp,
            ),
        )
        course_id = int(cursor.lastrowid)
    log_product_event(user_id, "medication_course_created", {"course_id": course_id})
    return course_id


def list_medication_courses(user_id: int, pet_id: int | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT medication_courses.*, pets.name AS pet_name
        FROM medication_courses
        JOIN pets ON pets.id = medication_courses.pet_id
        WHERE medication_courses.user_id = ?
    """
    params: list[Any] = [user_id]
    if pet_id:
        query += " AND medication_courses.pet_id = ?"
        params.append(pet_id)
    query += " ORDER BY medication_courses.created_at DESC"
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def mark_medication_given(user_id: int, course_id: int) -> None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM medication_courses WHERE id = ? AND user_id = ?",
            (course_id, user_id),
        ).fetchone()
        course = to_dict(row)
        if not course:
            return
        timestamp = now_iso()
        next_due = _next_med_due(timestamp, course["frequency"])
        status = "completed" if course["frequency"] == "once" else "active"
        end_date = parse_iso(course.get("end_date"))
        if end_date and next_due and parse_iso(next_due) and parse_iso(next_due) > end_date:
            next_due = None
            status = "completed"
        conn.execute(
            """
            UPDATE medication_courses
            SET last_given_at = ?, next_due_at = ?, status = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (timestamp, next_due, status, timestamp, course_id, user_id),
        )
    log_product_event(user_id, "medication_given", {"course_id": course_id})


def add_weight_log(user_id: int, pet_id: int, weight: float, measured_at: str, note: str) -> int:
    with connect() as conn:
        cursor = conn.execute(
            "INSERT INTO weight_logs (pet_id, user_id, weight, measured_at, note) VALUES (?, ?, ?, ?, ?)",
            (pet_id, user_id, weight, measured_at, note.strip()),
        )
        conn.execute("UPDATE pets SET weight = ?, updated_at = ? WHERE id = ? AND user_id = ?", (weight, now_iso(), pet_id, user_id))
        log_id = int(cursor.lastrowid)
    log_product_event(user_id, "weight_logged", {"pet_id": pet_id})
    return log_id


def list_weight_logs(user_id: int, pet_id: int | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT weight_logs.*, pets.name AS pet_name
        FROM weight_logs
        JOIN pets ON pets.id = weight_logs.pet_id
        WHERE weight_logs.user_id = ?
    """
    params: list[Any] = [user_id]
    if pet_id:
        query += " AND weight_logs.pet_id = ?"
        params.append(pet_id)
    query += " ORDER BY weight_logs.measured_at ASC"
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def add_expense(user_id: int, payload: dict[str, Any]) -> int:
    created_at = now_iso()
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO expenses (pet_id, user_id, category, amount, currency, spent_at, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["pet_id"],
                user_id,
                payload["category"],
                float(payload["amount"]),
                payload.get("currency", "USD"),
                payload["spent_at"],
                payload.get("note", "").strip(),
                created_at,
            ),
        )
        expense_id = int(cursor.lastrowid)
    log_product_event(user_id, "expense_added", {"expense_id": expense_id, "category": payload["category"]})
    return expense_id


def list_expenses(user_id: int, pet_id: int | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT expenses.*, pets.name AS pet_name
        FROM expenses
        JOIN pets ON pets.id = expenses.pet_id
        WHERE expenses.user_id = ?
    """
    params: list[Any] = [user_id]
    if pet_id:
        query += " AND expenses.pet_id = ?"
        params.append(pet_id)
    query += " ORDER BY expenses.spent_at DESC"
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def expense_summary(user_id: int, pet_id: int | None = None) -> dict[str, float]:
    params: list[Any] = [user_id]
    pet_filter = ""
    if pet_id:
        pet_filter = " AND pet_id = ?"
        params.append(pet_id)
    with connect() as conn:
        total_row = conn.execute(
            f"SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE user_id = ?{pet_filter}",
            params,
        ).fetchone()
        month_params = list(params)
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        month_row = conn.execute(
            f"SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE user_id = ?{pet_filter} AND spent_at >= ?",
            month_params + [month_start],
        ).fetchone()
    return {"all_time": float(total_row["total"]), "month": float(month_row["total"])}


def monthly_expense_rows(user_id: int, pet_id: int | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT substr(spent_at, 1, 7) AS month, COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = ?
    """
    params: list[Any] = [user_id]
    if pet_id:
        query += " AND pet_id = ?"
        params.append(pet_id)
    query += " GROUP BY substr(spent_at, 1, 7) ORDER BY month ASC"
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def create_document(user_id: int, payload: dict[str, Any]) -> int:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO documents (pet_id, user_id, type, file_url, file_name, uploaded_at, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["pet_id"],
                user_id,
                payload["type"],
                payload["file_url"],
                payload["file_name"],
                payload["uploaded_at"],
                payload.get("note", "").strip(),
            ),
        )
        doc_id = int(cursor.lastrowid)
    log_product_event(user_id, "document_uploaded", {"document_id": doc_id})
    return doc_id


def list_documents(user_id: int, pet_id: int | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT documents.*, pets.name AS pet_name
        FROM documents
        JOIN pets ON pets.id = documents.pet_id
        WHERE documents.user_id = ?
    """
    params: list[Any] = [user_id]
    if pet_id:
        query += " AND documents.pet_id = ?"
        params.append(pet_id)
    query += " ORDER BY documents.uploaded_at DESC"
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def create_support_ticket(user_id: int, subject: str, message: str) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO support_tickets (user_id, subject, message, created_at) VALUES (?, ?, ?, ?)",
            (user_id, subject.strip(), message.strip(), now_iso()),
        )


def list_support_tickets() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT support_tickets.*, users.email
            FROM support_tickets
            JOIN users ON users.id = support_tickets.user_id
            ORDER BY support_tickets.created_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def _notification_send_time(code: str, scheduled_at: datetime) -> datetime:
    if code == "3d":
        return scheduled_at - timedelta(days=3)
    if code == "1d":
        return scheduled_at - timedelta(days=1)
    if code == "12h":
        return scheduled_at - timedelta(hours=12)
    return scheduled_at


def _build_event_notification_message(event: dict[str, Any], pet_name: str) -> str:
    scheduled_at = parse_iso(event.get("scheduled_at"))
    when_text = scheduled_at.strftime("%b %d, %Y %H:%M") if scheduled_at else "soon"
    return f"Reminder: {event['title']} for {pet_name} is scheduled for {when_text}."


def _build_medication_notification_message(med: dict[str, Any], pet_name: str) -> str:
    due_at = parse_iso(med.get("next_due_at"))
    when_text = due_at.strftime("%b %d, %Y %H:%M") if due_at else "soon"
    return f"Medication reminder: {med['medicine_name']} for {pet_name} is due around {when_text}."


def sync_due_notifications(user_id: int) -> None:
    user = get_user(user_id)
    if not user:
        return
    now = datetime.utcnow().replace(microsecond=0)

    with connect() as conn:
        pets = {
            row["id"]: row["name"]
            for row in conn.execute("SELECT id, name FROM pets WHERE user_id = ?", (user_id,)).fetchall()
        }
        channels: list[str] = []
        if bool(user.get("notification_in_app")):
            channels.append("in_app")
        if bool(user.get("notification_email")):
            channels.append("email")

        events = conn.execute(
            "SELECT * FROM care_events WHERE user_id = ? AND status = 'planned'",
            (user_id,),
        ).fetchall()

        for event_row in events:
            event = dict(event_row)
            scheduled_at = parse_iso(event["scheduled_at"])
            if scheduled_at is None:
                continue
            reminder_codes = json.loads(event.get("reminder_settings") or "[]")
            for code in reminder_codes:
                send_at = _notification_send_time(code, scheduled_at)
                if send_at <= now:
                    pet_name = pets.get(event["pet_id"], "your pet")
                    message = _build_event_notification_message(event, pet_name)
                    for channel in channels:
                        exists = conn.execute(
                            """
                            SELECT id FROM notifications
                            WHERE user_id = ? AND event_id = ? AND send_at = ? AND channel = ?
                            """,
                            (user_id, event["id"], send_at.isoformat(), channel),
                        ).fetchone()
                        if exists is None:
                            conn.execute(
                                """
                                INSERT INTO notifications (user_id, pet_id, event_id, channel, send_at, status, message, created_at)
                                VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
                                """,
                                (user_id, event["pet_id"], event["id"], channel, send_at.isoformat(), message, now_iso()),
                            )

        meds = conn.execute(
            "SELECT * FROM medication_courses WHERE user_id = ? AND status = 'active' AND next_due_at IS NOT NULL",
            (user_id,),
        ).fetchall()
        for med_row in meds:
            med = dict(med_row)
            next_due = parse_iso(med["next_due_at"])
            if next_due and next_due <= now + timedelta(hours=12):
                pet_name = pets.get(med["pet_id"], "your pet")
                message = _build_medication_notification_message(med, pet_name)
                for channel in channels:
                    exists = conn.execute(
                        """
                        SELECT id FROM notifications
                        WHERE user_id = ? AND event_id IS NULL AND pet_id = ? AND send_at = ? AND channel = ? AND message = ?
                        """,
                        (user_id, med["pet_id"], med["next_due_at"], channel, message),
                    ).fetchone()
                    if exists is None:
                        conn.execute(
                            """
                            INSERT INTO notifications (user_id, pet_id, event_id, channel, send_at, status, message, created_at)
                            VALUES (?, ?, NULL, ?, ?, 'pending', ?, ?)
                            """,
                            (
                                user_id,
                                med["pet_id"],
                                channel,
                                med["next_due_at"],
                                message,
                                now_iso(),
                            ),
                        )


def list_notifications(user_id: int, only_pending: bool = True) -> list[dict[str, Any]]:
    sync_due_notifications(user_id)
    query = """
        SELECT notifications.*, pets.name AS pet_name, care_events.title AS event_title
        FROM notifications
        LEFT JOIN pets ON pets.id = notifications.pet_id
        LEFT JOIN care_events ON care_events.id = notifications.event_id
        WHERE notifications.user_id = ? AND notifications.channel = 'in_app'
    """
    params: list[Any] = [user_id]
    if only_pending:
        query += " AND notifications.status = 'pending'"
    query += " ORDER BY notifications.send_at ASC LIMIT 20"
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def mark_notification_read(user_id: int, notification_id: int) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE notifications SET status = 'read' WHERE id = ? AND user_id = ?",
            (notification_id, user_id),
        )


def dispatch_due_email_notifications(user_id: int | None = None) -> dict[str, int]:
    query = """
        SELECT notifications.*, users.email, users.name, pets.name AS pet_name, care_events.title AS event_title
        FROM notifications
        JOIN users ON users.id = notifications.user_id
        LEFT JOIN pets ON pets.id = notifications.pet_id
        LEFT JOIN care_events ON care_events.id = notifications.event_id
        WHERE notifications.channel = 'email'
          AND notifications.status = 'pending'
          AND notifications.send_at <= ?
          AND users.notification_email = 1
    """
    now = datetime.utcnow().replace(microsecond=0)
    params: list[Any] = [now.isoformat()]
    if user_id is not None:
        query += " AND notifications.user_id = ?"
        params.append(user_id)
    query += " ORDER BY notifications.send_at ASC"

    if not email_configured():
        with connect() as conn:
            pending = conn.execute(f"SELECT COUNT(*) AS count FROM ({query})", params).fetchone()
        return {"sent": 0, "failed": 0, "skipped": int(pending["count"])}

    sent = 0
    failed = 0

    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
        for row in rows:
            item = dict(row)
            pet_name = item.get("pet_name") or "your pet"
            title = item.get("event_title") or item.get("message") or "Pet reminder"
            subject = f"Pet Help AI reminder: {title}"
            text_body = (
                f"Hello {item.get('name') or ''},\n\n"
                f"{item['message']}\n\n"
                f"Pet: {pet_name}\n"
                f"Scheduled: {item['send_at']}\n\n"
                "Open Pet Help AI to view the full care timeline."
            ).strip()
            html_body = (
                f"<p>Hello {item.get('name') or ''},</p>"
                f"<p>{item['message']}</p>"
                f"<p><strong>Pet:</strong> {pet_name}<br/>"
                f"<strong>Scheduled:</strong> {item['send_at']}</p>"
                "<p>Open Pet Help AI to view the full care timeline.</p>"
            )
            try:
                send_email_message(item["email"], subject, text_body, html_body)
                conn.execute(
                    "UPDATE notifications SET status = 'sent' WHERE id = ?",
                    (item["id"],),
                )
                sent += 1
            except Exception:
                conn.execute(
                    "UPDATE notifications SET status = 'failed' WHERE id = ?",
                    (item["id"],),
                )
                failed += 1

    return {"sent": sent, "failed": failed, "skipped": 0}


def analytics_summary() -> dict[str, Any]:
    now = datetime.utcnow()
    one_day = (now - timedelta(days=1)).isoformat()
    seven_days = (now - timedelta(days=7)).isoformat()
    thirty_days = (now - timedelta(days=30)).isoformat()
    with connect() as conn:
        totals = {
            "users": int(conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]),
            "pets": int(conn.execute("SELECT COUNT(*) AS count FROM pets").fetchone()["count"]),
            "subscriptions": int(conn.execute("SELECT COUNT(*) AS count FROM subscriptions WHERE status IN ('trialing', 'active')").fetchone()["count"]),
            "tickets": int(conn.execute("SELECT COUNT(*) AS count FROM support_tickets WHERE status = 'open'").fetchone()["count"]),
            "dau": int(conn.execute("SELECT COUNT(DISTINCT user_id) AS count FROM product_events WHERE created_at >= ?", (one_day,)).fetchone()["count"]),
            "wau": int(conn.execute("SELECT COUNT(DISTINCT user_id) AS count FROM product_events WHERE created_at >= ?", (seven_days,)).fetchone()["count"]),
            "mau": int(conn.execute("SELECT COUNT(DISTINCT user_id) AS count FROM product_events WHERE created_at >= ?", (thirty_days,)).fetchone()["count"]),
        }
        rows = conn.execute(
            """
            SELECT event_name, COUNT(*) AS count
            FROM product_events
            GROUP BY event_name
            ORDER BY count DESC
            LIMIT 20
            """
        ).fetchall()
    return {"totals": totals, "events": [dict(row) for row in rows]}


def admin_users() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT users.id, users.name, users.email, users.timezone, users.role, users.created_at, users.updated_at,
                   subscriptions.plan, subscriptions.status
            FROM users
            LEFT JOIN subscriptions ON subscriptions.user_id = users.id
            ORDER BY users.created_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]
