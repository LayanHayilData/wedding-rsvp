# Wedding RSVP - Google Sheets Version

هذه نسخة تحفظ الردود في Google Sheets بدل SQLite/CSV، لذلك الردود لا تضيع عند Refresh أو إعادة تشغيل Streamlit.

## الملفات

- `app.py` تطبيق Streamlit.
- `guest_names.csv` أسماء المعازيم.
- `requirements.txt` المكتبات.
- `.streamlit/secrets.toml.example` مثال لإعدادات الأسرار.

## الخطوات السريعة

### 1) ارفعي الملفات إلى GitHub

استبدلي ملفات المستودع الحالي بهذه الملفات ثم:

```bash
git add .
git commit -m "Use Google Sheets database"
git push
```

### 2) جهزي Google Sheet

- افتحي Google Sheets.
- أنشئي ملف جديد باسم `Wedding RSVP`.
- انسخي Spreadsheet ID من الرابط.

مثال الرابط:

```text
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
```

### 3) جهزي Google Service Account

- ادخلي Google Cloud Console.
- أنشئي Project.
- فعلي Google Sheets API و Google Drive API.
- أنشئي Service Account.
- أنشئي Key بصيغة JSON.
- افتحي ملف JSON وانسخي محتواه.

### 4) شاركي Google Sheet مع service account

من ملف JSON، انسخي `client_email` وشاركي Google Sheet معه بصلاحية Editor.

### 5) ضعي Secrets في Streamlit Cloud

Streamlit app > Settings > Secrets

الصقي التالي مع تعديل القيم:

```toml
SPREADSHEET_ID = "ضع ID حق Google Sheet هنا"
ADMIN_PASSWORD = "غيري كلمة المرور هنا"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
```

### 6) افتحي الموقع

- صفحة الضيوف: الروابط الشخصية من لوحة المنظم.
- لوحة المنظم:

```text
https://YOUR-APP.streamlit.app/?admin=1
```

- صفحة الدخول:

```text
https://YOUR-APP.streamlit.app/?checkin=1
```

