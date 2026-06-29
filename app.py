
import csv
import io
import os
import secrets
import sqlite3
from datetime import datetime
from urllib.parse import quote

import qrcode
import streamlit as st
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)
DB_FILE = "wedding.db"
QR_FOLDER = "qr_codes"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "LayansEngagement2026")  # غيريها من Streamlit Secrets بعد النشر


def get_base_url():
    """Public website link used when exporting guest links."""
    try:
        value = st.secrets.get("PUBLIC_BASE_URL", "")
    except Exception:
        value = ""
    value = value or os.getenv("PUBLIC_BASE_URL", "http://localhost:8501")
    return value.rstrip("/")


BASE_URL = get_base_url()

os.makedirs(QR_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="دعوة زفاف",
    page_icon="💍",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #fffaf2 0%, #ffffff 55%, #f7ead2 100%);
        direction: rtl;
    }
    .main-card {
        background: rgba(255,255,255,0.88);
        padding: 28px;
        border-radius: 24px;
        border: 1px solid #ead7b7;
        box-shadow: 0 8px 28px rgba(151, 113, 51, 0.12);
        text-align: center;
        margin-bottom: 18px;
    }
    .title {
        color: #9b741d;
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .subtitle {
        color: #5f503a;
        font-size: 18px;
        line-height: 1.9;
    }
    .metric-card {
        background: white;
        padding: 14px;
        border-radius: 16px;
        border: 1px solid #ead7b7;
        text-align: center;
        margin: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db_if_missing():
    conn = connect()
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
    conn.close()


def get_guest_by_invite_token(token):
    conn = connect()
    guest = conn.execute("SELECT * FROM guests WHERE invite_token = ?", (token,)).fetchone()
    conn.close()
    return guest


def get_guest_by_qr_token(qr_token):
    conn = connect()
    guest = conn.execute("SELECT * FROM guests WHERE qr_token = ?", (qr_token,)).fetchone()
    conn.close()
    return guest


def accept_invitation(guest_id):
    conn = connect()
    guest = conn.execute("SELECT * FROM guests WHERE id = ?", (guest_id,)).fetchone()

    qr_token = guest["qr_token"]
    if not qr_token:
        qr_token = secrets.token_urlsafe(24)

    conn.execute(
        """
        UPDATE guests
        SET status = 'Attending', qr_token = ?, rsvp_time = ?
        WHERE id = ?
        """,
        (qr_token, now(), guest_id),
    )
    conn.commit()
    conn.close()
    return qr_token


def decline_invitation(guest_id):
    conn = connect()
    conn.execute(
        """
        UPDATE guests
        SET status = 'Not attending', qr_token = NULL, checked_in = 0, rsvp_time = ?, checkin_time = NULL
        WHERE id = ?
        """,
        (now(), guest_id),
    )
    conn.commit()
    conn.close()


def make_qr_image(qr_token):
    qr_path = os.path.join(QR_FOLDER, f"{qr_token}.png")
    if not os.path.exists(qr_path):
        img = qrcode.make(qr_token)
        img.save(qr_path)
    return qr_path


def get_all_guests():
    conn = connect()
    rows = conn.execute("SELECT * FROM guests ORDER BY id").fetchall()
    conn.close()
    return rows


def status_ar(status):
    if status == "Attending":
        return "✅ سيحضر"
    if status == "Not attending":
        return "❌ اعتذر"
    return "⏳ لم يرد"


def export_csv(rows, base_url=BASE_URL):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "status", "checked_in", "rsvp_time", "checkin_time", "personal_link"])
    for r in rows:
        link = f"{base_url.rstrip('/')}/?token={quote(r['invite_token'])}"
        writer.writerow([
            r["name"],
            r["status"],
            "Yes" if r["checked_in"] else "No",
            r["rsvp_time"] or "",
            r["checkin_time"] or "",
            link,
        ])
    return output.getvalue().encode("utf-8-sig")


def show_guest_page(token):
    guest = get_guest_by_invite_token(token)

    if not guest:
        st.error("الرابط غير صحيح أو غير موجود.")
        return

    st.markdown(
        f"""
        <div class="main-card">
            <div class="title">دعوة زفاف 🤍</div>
            <div class="subtitle">
                أهلًا {guest['name']}<br>
                يسرنا دعوتكم لحضور حفل الزفاف.<br>
                هل ستشرفوننا بالحضور؟
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if guest["status"] == "Attending" and guest["qr_token"]:
        st.success("تم تأكيد حضوركم مسبقًا 🤍 هذا رمز الدخول الخاص بكم.")
        st.image(make_qr_image(guest["qr_token"]), width=260)
        return

    if guest["status"] == "Not attending":
        st.info("تم تسجيل اعتذاركم. نسعد بدعواتكم الطيبة 🤍")
        return

    col1, col2 = st.columns(2)
    with col1:
        if st.button("نعم، سأحضر 🤍", use_container_width=True):
            qr_token = accept_invitation(guest["id"])
            st.success("شكراً لتأكيد حضوركم 🤍 هذا رمز الدخول الخاص بكم.")
            st.image(make_qr_image(qr_token), width=260)
            st.rerun()

    with col2:
        if st.button("أعتذر عن الحضور", use_container_width=True):
            decline_invitation(guest["id"])
            st.info("شكرًا لإبلاغنا. نسعد بدعواتكم الطيبة 🤍")
            st.rerun()


def password_gate():
    password = st.text_input("كلمة مرور المنظم", type="password")
    return password == ADMIN_PASSWORD


def show_admin_page():
    st.markdown("<div class='title'>لوحة المنظم</div>", unsafe_allow_html=True)
    if not password_gate():
        st.warning("أدخلي كلمة المرور لعرض لوحة المنظم.")
        return

    rows = get_all_guests()
    total = len(rows)
    attending = sum(1 for r in rows if r["status"] == "Attending")
    declined = sum(1 for r in rows if r["status"] == "Not attending")
    no_response = sum(1 for r in rows if r["status"] == "No response")
    checked = sum(1 for r in rows if r["checked_in"])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("الإجمالي", total)
    c2.metric("سيحضر", attending)
    c3.metric("اعتذر", declined)
    c4.metric("لم يرد", no_response)
    c5.metric("دخلوا", checked)

    public_url = st.text_input(
        "رابط الموقع العام لاستخدامه داخل الروابط الشخصية",
        value=BASE_URL,
        help="بعد نشر الموقع على Streamlit Cloud، الصقي رابط الموقع هنا ثم حملي ملف الروابط."
    ).rstrip("/")

    st.download_button(
        "تحميل ملف الحضور والروابط CSV",
        data=export_csv(rows, public_url),
        file_name="wedding_dashboard_links.csv",
        mime="text/csv",
        use_container_width=True,
    )

    search = st.text_input("بحث بالاسم")
    table = []
    for r in rows:
        if search and search.strip() not in r["name"]:
            continue
        table.append({
            "الاسم": r["name"],
            "الحالة": status_ar(r["status"]),
            "دخل الحفل": "✅" if r["checked_in"] else "❌",
            "وقت الرد": r["rsvp_time"] or "-",
            "وقت الدخول": r["checkin_time"] or "-",
            "الرابط الشخصي": f"{public_url}/?token={r['invite_token']}",
        })

    st.dataframe(table, use_container_width=True, hide_index=True)


def show_checkin_page():
    st.markdown("<div class='title'>تسجيل الدخول للحفل</div>", unsafe_allow_html=True)
    if not password_gate():
        st.warning("أدخلي كلمة المرور لفتح صفحة الدخول.")
        return

    scanned = st.text_input("امسحي QR أو الصقي الكود هنا")
    if scanned:
        scanned = scanned.strip()
        guest = get_guest_by_qr_token(scanned)

        if not guest:
            st.error("❌ الرمز غير صحيح. لا يسمح بالدخول.")
            return

        if guest["status"] != "Attending":
            st.error("❌ هذا الضيف لم يؤكد الحضور.")
            return

        if guest["checked_in"]:
            st.error(f"❌ تم استخدام هذا الرمز مسبقًا. لا يسمح بالدخول مرة أخرى. الاسم: {guest['name']}")
            return

        conn = connect()
        conn.execute(
            "UPDATE guests SET checked_in = 1, checkin_time = ? WHERE id = ?",
            (now(), guest["id"]),
        )
        conn.commit()
        conn.close()
        st.success(f"✅ أهلًا {guest['name']}، تم السماح بالدخول.")


def show_home():
    st.markdown(
        """
        <div class="main-card">
            <div class="title">نظام دعوات الزفاف 💍</div>
            <div class="subtitle">
                هذه الصفحة الرئيسية. افتحي رابط الضيف الشخصي لعرض الدعوة الخاصة به.<br>
                للمنظم: استخدمي الروابط التالية.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write(f"لوحة المنظم: {BASE_URL}/?admin=1")
    st.write(f"صفحة الدخول: {BASE_URL}/?checkin=1")


init_db_if_missing()
params = st.query_params

if "token" in params:
    show_guest_page(params["token"])
elif "admin" in params:
    show_admin_page()
elif "checkin" in params:
    show_checkin_page()
else:
    show_home()
