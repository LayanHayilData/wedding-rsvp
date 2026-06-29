import io
import uuid
from datetime import datetime

import pandas as pd
import qrcode
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="دعوة زفاف", page_icon="🤍", layout="centered")

# Hide most Streamlit default UI elements
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}
[data-testid="stHeader"] {display: none !important;}
.viewerBadge_container__1QSob {display: none !important;}

html, body, [class*="css"] {
    direction: rtl;
    text-align: center;
    font-family: "Arial", sans-serif;
}
.stApp {
    background: linear-gradient(180deg, #fffaf2 0%, #ffffff 55%, #fff8ec 100%);
}
.invite-card {
    background: rgba(255,255,255,0.92);
    border: 1px solid #ead6af;
    border-radius: 24px;
    padding: 42px 30px;
    margin: 20px auto 20px auto;
    max-width: 760px;
    box-shadow: 0 20px 50px rgba(143, 103, 34, 0.10);
}
.title {
    color: #a6791b;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 10px;
}
.subtitle {
    color: #4d3b2a;
    font-size: 19px;
    line-height: 2;
}
.small-note {
    color: #806a4a;
    font-size: 15px;
}
.success-box {
    background: #f7fff7;
    border: 1px solid #b9e0b9;
    border-radius: 18px;
    padding: 22px;
    margin-top: 18px;
}
.warning-box {
    background: #fff8f0;
    border: 1px solid #edd3b2;
    border-radius: 18px;
    padding: 22px;
    margin-top: 18px;
}
</style>
""", unsafe_allow_html=True)

SHEET_NAME = "guests"
COLUMNS = [
    "guest_id", "name", "token", "status", "qr_code",
    "checked_in", "responded_at", "checked_in_at"
]
import base64

def set_background(image_path):
    with open(image_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    .main-card {{
        background: rgba(255, 255, 255, 0.72);
        padding: 35px;
        border-radius: 25px;
        max-width: 650px;
        margin: auto;
        text-align: center;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    }}

    h1 {{
        color: #8b7a58;
        font-size: 52px;
        text-align: center;
        font-family: serif;
    }}

    .subtitle {{
        color: #8b7a58;
        font-size: 22px;
        text-align: center;
        line-height: 2;
    }}

    .stButton > button {{
        background-color: #b7a27a;
        color: white;
        border-radius: 25px;
        border: none;
        padding: 12px 35px;
        font-size: 18px;
    }}
    </style>
    """, unsafe_allow_html=True)
    set_background("background.jpg")

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@st.cache_resource(show_spinner=False)
def get_worksheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(st.secrets["SPREADSHEET_ID"])
    try:
        ws = spreadsheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=SHEET_NAME, rows=300, cols=len(COLUMNS))
        ws.append_row(COLUMNS)
    return ws


def load_df():
    ws = get_worksheet()
    records = ws.get_all_records()
    if not records:
        return pd.DataFrame(columns=COLUMNS)
    df = pd.DataFrame(records)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNS]


def save_df(df):
    df = df.fillna("")
    ws = get_worksheet()
    ws.clear()
    ws.update([COLUMNS] + df[COLUMNS].astype(str).values.tolist())


def init_guests_if_needed():
    df = load_df()
    if len(df) > 0:
        return df

    names = pd.read_csv("guest_names.csv", header=None)[0].dropna().astype(str).str.strip()
    names = names[names != ""].drop_duplicates().reset_index(drop=True)

    rows = []
    for i, name in enumerate(names, start=1):
        token = uuid.uuid4().hex[:22]
        rows.append({
            "guest_id": f"GUEST-{i:03d}",
            "name": name,
            "token": token,
            "status": "No Response",
            "qr_code": "",
            "checked_in": "No",
            "responded_at": "",
            "checked_in_at": "",
        })
    df = pd.DataFrame(rows, columns=COLUMNS)
    save_df(df)
    return df


def qr_image_bytes(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def get_query_param(key):
    value = st.query_params.get(key, "")
    if isinstance(value, list):
        return value[0] if value else ""
    return value


def update_guest(token, **updates):
    df = load_df()
    idx = df.index[df["token"].astype(str) == str(token)]
    if len(idx) == 0:
        return False
    i = idx[0]
    for k, v in updates.items():
        if k in df.columns:
            df.loc[i, k] = v
    save_df(df)
    return True


def page_guest(token):
    df = init_guests_if_needed()
    match = df[df["token"].astype(str) == str(token)]

    if match.empty:
        st.error("الرابط غير صحيح أو غير موجود.")
        return

    guest = match.iloc[0]
    name = guest["name"]
    status = str(guest["status"])
    qr_code = str(guest["qr_code"])
       st.markdown(f"""
        <div class="invite-card" dir="rtl">
        
            <div class="title">بسم الله الرحمن الرحيم</div>
        
            <div class="subtitle">
                بكل الفرح والسرور<br><br>
        
                يتشرف العروسان بدعوتكم<br>
                <b>{name}</b><br><br>
        
                لمشاركتهم فرحة عقد القران
                وحضور حفل الملكة،
                سائلين الله أن يبارك لهم ويتمم لهم على خير.
            </div>
        
        </div>
        """, unsafe_allow_html=True)
    if status == "Attending" and qr_code:
        st.markdown("<div class='success-box'>تم تأكيد حضوركم مسبقًا 🤍<br>هذا رمز الدخول الخاص بكم.</div>", unsafe_allow_html=True)
        st.image(qr_image_bytes(qr_code), width=260)
        return

    if status == "Not Attending":
        st.markdown("<div class='warning-box'>شكرًا لإبلاغنا 🤍<br>أذكرونا بدعوة طيبة.</div>", unsafe_allow_html=True)
        return

    col1, col2 = st.columns(2)
    with col1:
        if st.button("نعم، سأحضر 🤍", use_container_width=True):
            qr_code = f"WEDDING-{token}"
            update_guest(token, status="Attending", qr_code=qr_code, responded_at=now_str())
            st.rerun()
    with col2:
        if st.button("أعتذر عن الحضور", use_container_width=True):
            update_guest(token, status="Not Attending", qr_code="", responded_at=now_str())
            st.rerun()


def page_admin():
    st.title("لوحة المنظم")
    password = st.text_input("كلمة المرور", type="password")
    if password != st.secrets.get("ADMIN_PASSWORD", "1234"):
        st.stop()

    df = init_guests_if_needed()

    total = len(df)
    attending = (df["status"] == "Attending").sum()
    declined = (df["status"] == "Not Attending").sum()
    no_response = (df["status"] == "No Response").sum()
    checked = (df["checked_in"] == "Yes").sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("الإجمالي", total)
    c2.metric("سيحضر", attending)
    c3.metric("اعتذر", declined)
    c4.metric("لم يرد", no_response)
    c5.metric("تم الدخول", checked)

    st.subheader("توليد روابط المعازيم")
    base_url = st.text_input("رابط الموقع العام", value="https://wedding-rsvp-qvkmwn6ca7wmeynuyndi7r.streamlit.app")
    links_df = df[["guest_id", "name", "status", "checked_in"]].copy()
    links_df["personal_link"] = links_df["guest_id"].map(lambda _: "")
    links_df["personal_link"] = df["token"].apply(lambda t: f"{base_url.rstrip('/')}/?token={t}")

    csv = links_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "تحميل ملف روابط المعازيم CSV",
        data=csv,
        file_name="guest_links.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.subheader("جدول المعازيم")
    search = st.text_input("بحث بالاسم")
    view_df = df.copy()
    if search:
        view_df = view_df[view_df["name"].astype(str).str.contains(search, case=False, na=False)]
    st.dataframe(view_df[["guest_id", "name", "status", "checked_in", "responded_at", "checked_in_at"]], use_container_width=True)

    st.download_button(
        "تحميل كل البيانات CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="wedding_responses.csv",
        mime="text/csv",
        use_container_width=True,
    )


def page_checkin():
    st.title("تسجيل دخول الحفل")
    password = st.text_input("كلمة مرور المنظم", type="password")
    if password != st.secrets.get("ADMIN_PASSWORD", "1234"):
        st.stop()

    scanned = st.text_input("امسح/اكتب رمز QR هنا")
    if not scanned:
        st.info("انتظار مسح الرمز...")
        return

    df = load_df()
    match = df[df["qr_code"].astype(str) == str(scanned).strip()]
    if match.empty:
        st.error("رمز غير صحيح. لا يسمح بالدخول.")
        return

    idx = match.index[0]
    guest = df.loc[idx]
    if guest["checked_in"] == "Yes":
        st.error(f"تم استخدام هذا الرمز مسبقًا. لا يسمح بالدخول. الاسم: {guest['name']}")
        return

    df.loc[idx, "checked_in"] = "Yes"
    df.loc[idx, "checked_in_at"] = now_str()
    save_df(df)
    st.success(f"أهلًا {guest['name']} 🤍 تم السماح بالدخول.")


def page_home():
    st.markdown("""
    <div class="invite-card">
        <div class="title">🤍 دعوة زفاف</div>
        <div class="subtitle">
            الرجاء استخدام الرابط الشخصي المرسل لكم لتأكيد الحضور.
        </div>
        <div class="small-note">هذا الرابط خاص بكل معزوم.</div>
    </div>
    """, unsafe_allow_html=True)


try:
    token = get_query_param("token")
    admin = get_query_param("admin")
    checkin = get_query_param("checkin")

    if admin == "1":
        page_admin()
    elif checkin == "1":
        page_checkin()
    elif token:
        page_guest(token)
    else:
        page_home()
except Exception as e:
    st.error("حدث خطأ في إعدادات التطبيق. تأكدي من وضع Secrets الخاصة بـ Google Sheets في Streamlit Cloud.")
    st.caption(str(e))
