# Wedding RSVP Public Version

هذه النسخة مخصصة حتى تشتغل الروابط عند الناس، وليس فقط على جهازك.

## التشغيل المحلي

```bash
cd WeddingRSVP_Public
pip install -r requirements.txt
python create_links.py
streamlit run app.py
```

الرابط المحلي يكون لك فقط:

```text
http://localhost:8501
```

## النشر حتى تفتح الروابط عند المعازيم

1. ارفعي هذا المجلد على GitHub.
2. افتحي Streamlit Community Cloud.
3. اختاري New app.
4. اختاري ملف `app.py`.
5. بعد النشر سيظهر لك رابط عام مثل:

```text
https://your-wedding-rsvp.streamlit.app
```

## توليد الروابط العامة للمعازيم

بعد ما تحصلين على رابط Streamlit العام، عندك طريقتين:

### الطريقة الأسهل من داخل الموقع

افتحي لوحة المنظم:

```text
https://your-wedding-rsvp.streamlit.app/?admin=1
```

كلمة المرور الافتراضية:

```text
1234
```

الصقي رابط الموقع العام في خانة: **رابط الموقع العام**، ثم حملي ملف CSV.
هذا الملف يحتوي على الرابط الشخصي لكل معزوم.

### طريقة التيرمنال

```bash
python create_links.py --base-url "https://your-wedding-rsvp.streamlit.app"
```

سيتم تحديث ملف:

```text
guest_links.csv
```

## روابط مهمة

صفحة المنظم:

```text
https://your-wedding-rsvp.streamlit.app/?admin=1
```

صفحة الدخول يوم الحفل:

```text
https://your-wedding-rsvp.streamlit.app/?checkin=1
```

## ملاحظة مهمة

SQLite مناسب كبداية وبسيط جدًا، لكن في Streamlit Cloud البيانات ممكن تتأثر إذا التطبيق أعيد تشغيله أو إذا عملت Redeploy. لذلك حملي ملف الحضور من لوحة المنظم بشكل متكرر كنسخة احتياطية.

إذا تبغين نسخة أقوى للمناسبة الحقيقية، استخدمي Google Sheets أو Supabase كقاعدة بيانات ثابتة.
