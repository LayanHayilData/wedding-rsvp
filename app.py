import streamlit as st
import pandas as pd
import qrcode
import base64
import io
from datetime import datetime
from pathlib import Path

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="ملكة أحمد وليان",
    page_icon="🤍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# Helpers
# =========================
def image_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def make_qr(data: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#4f4f4f", back_color="white").convert("RGB")
    return image_to_base64(img)


def save_local_row(row: dict):
    path = Path("rsvp_responses.csv")
    df_new = pd.DataFrame([row])
    if path.exists():
        df_old = pd.read_csv(path)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(path, index=False)


# =========================
# CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Tajawal:wght@400;500;700;800&display=swap');

html, body, [class*="css"] {
    direction: rtl;
}

.stApp {
    background:
        linear-gradient(rgba(255,255,255,0.58), rgba(255,255,255,0.58)),
        repeating-linear-gradient(90deg, rgba(180,170,155,0.18) 0px, rgba(180,170,155,0.18) 1px, transparent 1px, transparent 7px),
        repeating-linear-gradient(0deg, rgba(180,170,155,0.13) 0px, rgba(180,170,155,0.13) 1px, transparent 1px, transparent 7px),
        #f6f2eb;
}

.block-container {
    max-width: 760px;
    padding-top: 2.4rem;
    padding-bottom: 3rem;
}

/* Hide Streamlit default elements */
#MainMenu, footer, header {visibility: hidden;}

.invitation-card {
    width: 100%;
    max-width: 650px;
    margin: 0 auto;
    padding: 10px 18px 28px;
    text-align: center;
    color: #77736e;
}

.ornament {
    font-size: 34px;
    color: #77736e;
    letter-spacing: 6px;
    margin: 0 auto 18px;
    line-height: 1;
}

.top-line {
    font-family: 'Amiri', serif;
    font-size: 25px;
    line-height: 1.9;
    color: #77736e;
    margin-bottom: 30px;
}

.blessing {
    font-family: 'Tajawal', sans-serif;
    font-size: 20px;
    color: #77736e;
    margin: 10px 0 22px;
}

.monogram {
    font-family: 'Amiri', serif;
    font-size: 82px;
    font-weight: 700;
    color: #77736e;
    line-height: 0.95;
    margin: 8px 0 12px;
}

.date {
    font-family: 'Tajawal', sans-serif;
    font-size: 17px;
    letter-spacing: 5px;
    color: #77736e;
    margin-bottom: 8px;
    direction: ltr;
}

.names {
    font-family: 'Tajawal', sans-serif;
    font-size: 21px;
    color: #77736e;
    margin-bottom: 24px;
}

.duaa {
    font-family: 'Amiri', serif;
    font-size: 24px;
    line-height: 1.8;
    color: #77736e;
    margin: 16px auto 28px;
    max-width: 520px;
}

.form-box {
    max-width: 560px;
    margin: 22px auto 20px;
    padding: 24px 22px;
    border-radius: 22px;
    background: rgba(255,255,255,0.42);
    border: 1px solid rgba(130,120,105,0.13);
    box-shadow: 0 8px 24px rgba(90,80,70,0.06);
}

.form-title {
    font-family: 'Tajawal', sans-serif;
    font-size: 21px;
    font-weight: 700;
    color: #68635f;
    margin-bottom: 8px;
    text-align: center;
}

.form-note {
    font-family: 'Tajawal', sans-serif;
    font-size: 16px;
    color: #77736e;
    margin-bottom: 18px;
    text-align: center;
}

.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
    direction: rtl !important;
    text-align: right !important;
    border-radius: 14px !important;
    font-family: 'Tajawal', sans-serif !important;
}

.stButton > button {
    width: 100%;
    border-radius: 16px;
    border: 0;
    padding: 0.8rem 1rem;
    background: #77736e;
    color: white;
    font-family: 'Tajawal', sans-serif;
    font-size: 17px;
    font-weight: 700;
}

.stButton > button:hover {
    background: #625e5a;
    color: white;
}

/* Confirmation + QR section: fixed alignment */
.confirm-wrapper {
    width: 100%;
    max-width: 620px;
    margin: 34px auto 34px;
    padding: 0 8px;
    box-sizing: border-box;
    clear: both;
}

.confirm-grid {
    display: grid;
    grid-template-columns: 1fr 175px;
    align-items: center;
    column-gap: 26px;
    row-gap: 18px;
    width: 100%;
    box-sizing: border-box;
    padding: 22px 22px;
    border-radius: 24px;
    background: rgba(255,255,255,0.38);
    border: 1px solid rgba(130,120,105,0.12);
    box-shadow: 0 8px 24px rgba(90,80,70,0.05);
    direction: rtl;
}

.confirm-text {
    text-align: right;
    font-family: 'Tajawal', sans-serif;
    color: #5f5a56;
    min-width: 0;
}

.confirm-text h3 {
    margin: 0 0 12px;
    font-size: 23px;
    font-weight: 800;
    line-height: 1.5;
    color: #5d5853;
}

.confirm-text p {
    margin: 0 0 12px;
    font-size: 18px;
    font-weight: 600;
    line-height: 1.7;
}

.confirm-text .gate-note {
    margin-top: 20px;
    font-size: 14px;
    font-weight: 500;
    color: #77736e;
}

.qr-holder {
    width: 175px;
    height: 175px;
    justify-self: center;
    align-self: center;
    background: #ffffff;
    border-radius: 16px;
    padding: 12px;
    box-sizing: border-box;
    box-shadow: 0 3px 14px rgba(80,75,70,0.10);
}

.qr-holder img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.bottom-duaa {
    font-family: 'Amiri', serif;
    text-align: center;
    color: #77736e;
    font-size: 24px;
    margin: 36px auto 8px;
}

.bottom-ornament {
    text-align: center;
    font-size: 32px;
    color: #77736e;
    letter-spacing: 5px;
    margin-top: 6px;
}

/* Mobile alignment */
@media (max-width: 640px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1.2rem;
    }

    .invitation-card {
        padding: 6px 2px 20px;
    }

    .top-line {
        font-size: 22px;
        line-height: 1.75;
        margin-bottom: 24px;
    }

    .blessing {
        font-size: 18px;
    }

    .monogram {
        font-size: 72px;
    }

    .duaa {
        font-size: 21px;
        line-height: 1.7;
        margin-bottom: 24px;
    }

    .confirm-wrapper {
        margin: 28px auto 30px;
        padding: 0;
    }

    .confirm-grid {
        grid-template-columns: 1fr;
        padding: 22px 18px;
        row-gap: 18px;
        text-align: center;
    }

    .confirm-text {
        text-align: center;
        width: 100%;
    }

    .confirm-text h3 {
        font-size: 22px;
        margin-bottom: 10px;
    }

    .confirm-text p {
        font-size: 17px;
        margin-bottom: 8px;
    }

    .confirm-text .gate-note {
        margin-top: 16px;
        font-size: 14px;
    }

    .qr-holder {
        width: 170px;
        height: 170px;
        margin: 0 auto;
    }

    .bottom-duaa {
        font-size: 22px;
        margin-top: 34px;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================
# Main Invitation
# =========================
st.markdown("""
<div class="invitation-card" dir="rtl">
    <div class="ornament">⌁ ❦ ⌁</div>

    <div class="top-line">
        في ليلة يتكامل الفرح<br>
        والسرور
    </div>

    <div class="blessing">تم بحمد الله و نعمته عقد قراني</div>

    <div class="monogram">ل أ</div>

    <div class="date">9.10.2026</div>
    <div class="names">أحمــد & ليــان</div>

    <div class="duaa">
        اللهم بارك لهما وبارك عليهما<br>
        واجمع بينهما في خير<br>
        و أتمم علينا سعادتنا و أرزقنا التمام الجميل
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# Session State
# =========================
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False
if "guest_name" not in st.session_state:
    st.session_state.guest_name = ""
if "guest_count" not in st.session_state:
    st.session_state.guest_count = 1
if "qr_base64" not in st.session_state:
    st.session_state.qr_base64 = ""

# =========================
# RSVP Form / Confirmation
# =========================
if not st.session_state.confirmed:
    st.markdown('<div class="form-box" dir="rtl">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">تأكيد الحضور</div>', unsafe_allow_html=True)
    st.markdown('<div class="form-note">يرجى إدخال بياناتكم أدناه</div>', unsafe_allow_html=True)

    with st.form("rsvp_form", clear_on_submit=False):
        name = st.text_input("الاسم الكريم", placeholder="اكتبي الاسم هنا")
        phone = st.text_input("رقم الجوال", placeholder="05xxxxxxxx")
        guests = st.number_input("عدد الحضور", min_value=1, max_value=10, value=1, step=1)
        submit = st.form_submit_button("تأكيد الحضور")

    st.markdown('</div>', unsafe_allow_html=True)

    if submit:
        if not name.strip():
            st.warning("فضلاً أدخلي الاسم.")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            qr_data = f"Wedding RSVP | Name: {name.strip()} | Guests: {guests} | Time: {timestamp}"
            qr_base64 = make_qr(qr_data)

            row = {
                "timestamp": timestamp,
                "name": name.strip(),
                "phone": phone.strip(),
                "guests": int(guests),
                "qr_data": qr_data,
            }
            try:
                save_local_row(row)
            except Exception:
                pass

            st.session_state.confirmed = True
            st.session_state.guest_name = name.strip()
            st.session_state.guest_count = int(guests)
            st.session_state.qr_base64 = qr_base64
            st.rerun()

else:
    st.markdown(f"""
    <div class="confirm-wrapper" dir="rtl">
        <div class="confirm-grid">
            <div class="confirm-text">
                <h3>🤍 تم تأكيد حضوركم بنجاح</h3>
                <p>يسعدنا مشاركتكم لنا هذه المناسبة</p>
                <p class="gate-note">يرجى إبراز هذا الرمز عند بوابة الدخول</p>
            </div>

            <div class="qr-holder">
                <img src="data:image/png;base64,{st.session_state.qr_base64}" alt="QR Code">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="bottom-duaa">اعمروني بدعواتكم الصادقة</div>
<div class="bottom-ornament">⌁ ❦ ⌁</div>
""", unsafe_allow_html=True)
