import io
import uuid
import base64
from datetime import datetime

import pandas as pd
import qrcode
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


st.set_page_config(page_title="دعوة", page_icon="🤍", layout="centered")

SHEET_NAME = "guests"

COLUMNS = [
    "guest_id", "name", "token", "status", "qr_code",
    "checked_in", "responded_at", "checked_in_at"
]


def set_page_style(image_path="background.jpg"):
    try:
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()

        app_background = f"""
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center top;
            background-repeat: no-repeat;
            background-attachment: scroll;
            background-color: #f8f6f0;
        """
    except FileNotFoundError:
        app_background = """
            background: #f8f6f0;
        """

    st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display: none !important;}}
    [data-testid="stToolbar"] {{display: none !important;}}
    [data-testid="stDecoration"] {{display: none !important;}}
    [data-testid="stStatusWidget"] {{display: none !important;}}
    [data-testid="stHeader"] {{display: none !important;}}

    html, body, [class*="css"] {{
        direction: rtl;
        text-align: center;
        font-family: "Arial", sans-serif;
    }}

    .stApp {{
        {app_background}
    }}

    .block-container {{
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
        min-height: 100vh;
    }}

    div[data-testid="stVerticalBlock"] {{
        gap: 0.3rem;
    }}

    .rsvp-area {{
        width: min(82vw, 620px);
        margin: 445px auto 0 auto;
        padding: 0 12px;
        text-align: center;
        direction: rtl;
        color: #666666;
    }}

    .guest-name {{
        color: #666666;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
        line-height: 1.8;
    }}

    .rsvp-text {{
        color: #6d6d6d;
        font-size: 21px;
        line-height: 2;
        font-weight: 500;
        margin-bottom: 16px;
    }}

    .success-text {{
        color: #666666;
        font-size: 22px;
        line-height: 2;
        font-weight: 600;
        margin: 10px auto 8px auto;
    }}

    .qr-note {{
        color: #777777;
        font-size: 15px;
        line-height: 1.8;
        margin-top: 8px;
    }}

    .sorry-text {{
        color: #666666;
        font-size: 22px;
        line-height: 2;
        font-weight: 600;
        margin-top: 18px;
    }}

    .home-text {{
        width: min(82vw, 620px);
        margin: 445px auto 0 auto;
        color: #666666;
        font-size: 21px;
        line-height: 2;
        font-weight: 500;
        text-align: center;
    }}

    .admin-wrap {{
        background: rgba(255, 255, 255, 0.90);
        border: 1px solid rgba(160, 160, 160, 0.25);
        border-radius: 20px;
        padding: 24px;
        margin: 40px auto;
        max-width: 1100px;
        text-align: right;
    }}

    .stButton > button {{
        background-color: transparent;
        color: #666666;
        border: 1.5px solid #9a9a9a;
        border-radius: 0;
        padding: 10px 30px;
        font-size: 18px;
        font-weight: 600;
        box-shadow: none;
        min-height: 45px;
    }}

    .stButton > button:hover {{
        background-color: rgba(255, 255, 255, 0.35);
        color: #444444;
        border: 1.5px solid #666666;
    }}

    div[data-testid="stImage"] {{
        display: flex;
        justify-content: center;
        margin-top: 2px;
        margin-bottom: 0;
    }}

    div[data-testid="stImage"] img {{
        border: 1px solid rgba(110, 110, 110, 0.18);
        padding: 8px;
        background: rgba(255, 255, 255, 0.55);
        max-width: 190px !important;
    }}

    input, textarea {{
        text-align: right !important;
        direction: rtl !important;
    }}

    @media (max-width: 600px) {{
        .stApp {{
            background-size: 100% auto;
        }}

        .rsvp-area,
        .home-text {{
            margin-top: 300px;
            width: 88vw;
        }}

        .guest-name {{
            font-size: 22px;
        }}

        .rsvp-text,
        .success-text,
        .sorry-text,
        .home-text {{
            font-size: 17px;
            line-height: 1.9;
        }}

        .qr-note {{
            font-size: 13px;
        }}

        .stButton > button {{
            font-size: 15px;
            padding: 8px 14px;
        }}

        div[data-testid="stImage"] img {{
            max-width: 150px !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


set_page_style("background.jpg")


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@st.cache_resource(show_spinner=False)
def get_worksheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
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

    names = (
        pd.read_csv("guest_names.csv", header=None)[0]
        .dropna()
        .astype(str)
        .str.strip()
    )

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
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#555555", back_color="white")

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
    <div class="rsvp-area" dir="rtl">
        <div class="guest-name">أهلًا وسهلًا {name}</div>
    """, unsafe_allow_html=True)

    if status == "Attending" and qr_code:
        st.markdown(
            """
            <div class="success-text">
                تم تأكيد حضوركم بنجاح 🤍<br>
                يسعدنا مشاركتكم لنا هذه المناسبة
            </div>
            """,
            unsafe_allow_html=True
        )
        st.image(qr_image_bytes(qr_code), width=180)
        st.markdown(
            """
            <div class="qr-note">
                يرجى إبراز هذا الرمز عند بوابة الدخول
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    if status == "Not Attending":
        st.markdown(
            """
            <div class="sorry-text">
                شكرًا لإبلاغنا 🤍<br>
                أذكرونا بدعوة طيبة
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    st.markdown(
        """
        <div class="rsvp-text">
            نرجو منكم تأكيد الحضور
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("نعم، سأحضر", use_container_width=True):
            qr_code = f"MALKA-{token}"
            update_guest(
                token,
                status="Attending",
                qr_code=qr_code,
                responded_at=now_str()
            )
            st.rerun()

    with col2:
        if st.button("أعتذر عن الحضور", use_container_width=True):
            update_guest(
                token,
                status="Not Attending",
                qr_code="",
                responded_at=now_str()
            )
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def page_admin():
    st.markdown("<div class='admin-wrap'>", unsafe_allow_html=True)

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

    base_url = st.text_input(
        "رابط الموقع العام",
        value="https://wedding-rsvp-qvkmwn6ca7wmeynuyndi7r.streamlit.app"
    )

    links_df = df[["guest_id", "name", "status", "checked_in"]].copy()
    links_df["personal_link"] = df["token"].apply(
        lambda t: f"{base_url.rstrip('/')}/?token={t}"
    )

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
        view_df = view_df[
            view_df["name"].astype(str).str.contains(search, case=False, na=False)
        ]

    st.dataframe(
        view_df[[
            "guest_id", "name", "status",
            "checked_in", "responded_at", "checked_in_at"
        ]],
        use_container_width=True
    )

    st.download_button(
        "تحميل كل البيانات CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="malka_responses.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


def page_checkin():
    st.markdown("<div class='admin-wrap'>", unsafe_allow_html=True)

    st.title("تسجيل دخول الملكة")

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

    st.markdown("</div>", unsafe_allow_html=True)


def page_home():
    st.markdown("""
    <div class="home-text" dir="rtl">
        الرجاء استخدام الرابط الشخصي المرسل لكم لتأكيد الحضور.<br>
        هذا الرابط خاص بكل معزوم.
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
