import argparse
import csv
import os
import secrets
import sqlite3
from urllib.parse import quote

DB_FILE = "wedding.db"
NAMES_FILE = "اسماء-المعازيم.csv"
LINKS_FILE = "guest_links.csv"
BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8501")  # ضعي رابط الموقع العام هنا أو استخدمي --base-url


def clean_name(value: str) -> str:
    return (value or "").strip()


def read_names(path: str):
    names = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            name = clean_name(row[0])
            if name:
                names.append(name)
    return names


def init_db(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            invite_token TEXT UNIQUE NOT NULL,
            qr_token TEXT UNIQUE,
            status TEXT NOT NULL DEFAULT 'No response',
            checked_in INTEGER NOT NULL DEFAULT 0,
            rsvp_time TEXT,
            checkin_time TEXT
        )
        """
    )
    conn.commit()


def guest_count(conn):
    return conn.execute("SELECT COUNT(*) FROM guests").fetchone()[0]


def create_guest(conn, name):
    invite_token = secrets.token_urlsafe(16)
    conn.execute(
        "INSERT INTO guests (name, invite_token) VALUES (?, ?)",
        (name, invite_token),
    )


def export_links(conn, base_url: str):
    rows = conn.execute(
        "SELECT id, name, invite_token FROM guests ORDER BY id"
    ).fetchall()

    with open(LINKS_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["guest_id", "name", "personal_link", "whatsapp_message"])
        for guest_id, name, token in rows:
            link = f"{base_url}/?token={quote(token)}"
            msg = f"يسرنا دعوتك لحضور حفل الزفاف 🤍\nرابط الدعوة الخاص بك:\n{link}"
            writer.writerow([guest_id, name, link, msg])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL, help="رابط الموقع العام بعد النشر")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    if not os.path.exists(NAMES_FILE):
        raise FileNotFoundError(f"لم أجد ملف الأسماء: {NAMES_FILE}")

    names = read_names(NAMES_FILE)
    conn = sqlite3.connect(DB_FILE)
    init_db(conn)

    existing = guest_count(conn)
    added = 0

    # مهم: لا نضيف الأسماء مرة ثانية إذا قاعدة البيانات موجودة، حتى لا تتغير الروابط.
    # إذا تبغين إعادة توليد كل شيء، احذفي wedding.db ثم شغلي هذا الملف مرة أخرى.
    if existing == 0:
        for name in names:
            create_guest(conn, name)
            added += 1
        conn.commit()

    export_links(conn, base_url)
    total_db = guest_count(conn)
    conn.close()

    print("تم تجهيز قاعدة البيانات.")
    print(f"عدد الأسماء في ملف CSV: {len(names)}")
    print(f"عدد الضيوف في قاعدة البيانات: {total_db}")
    print(f"تمت إضافة أسماء جديدة: {added}")
    print(f"تم إنشاء/تحديث ملف الروابط: {LINKS_FILE}")


if __name__ == "__main__":
    main()
