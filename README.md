# سالن آرایشی - Salon Management System

سیستم مدیریت سالن آرایشی با Django و Python

## ویژگی‌ها

- احراز هویت با شماره موبایل
- ۴ نقش کاربری: مدیر، منشی، کارکن، مشتری
- سیستم رزرو نوبت هوشمند
- جلوگیری از تداخل نوبت‌ها
- لغو نوبت با محدودیت ۲۴ ساعت
- پنل مدیریت کامل برای هر نقش

## تکنولوژی‌ها

- Python 3.12+
- Django 6.0
- Django REST Framework
- PostgreSQL (Docker)
- HTML/CSS (بدون فریمورک خارجی)

## نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.12+
- Docker & Docker Compose
- Git

### مراحل نصب

1. کلون کردن پروژه:
\```bash
git clone <repository-url>
cd salon_project
\```

2. ساخت محیط مجازی:
\```bash
python -m venv venv
source venv/bin/activate
\```

3. نصب وابستگی‌ها:
\```bash
pip install -r requirements.txt
\```

4. ساخت فایل `.env`:
\```bash
cp .env.example .env
# ویرایش فایل .env با مقادیر مناسب
\```

5. راه‌اندازی دیتابیس:
\```bash
docker compose up -d
python manage.py migrate
\```

6. ساخت superuser:
\```bash
python manage.py createsuperuser
\```

7. اجرای سرور:
\```bash
python manage.py runserver
\```

## ساختار پروژه

\```
salon_project/
├── apps/
│   ├── accounts/      # احراز هویت و کاربران
│   ├── appointments/  # سیستم نوبت‌دهی
│   ├── dashboard/     # پنل‌های کاربری
│   ├── public/        # صفحات عمومی
│   ├── services/      # خدمات و دسته‌بندی‌ها
│   └── staff/         # کارکنان و برنامه کاری
├── config/            # تنظیمات Django
├── static/            # فایل‌های استاتیک
├── templates/         # قالب‌های HTML
├── docker-compose.yml
├── manage.py
└── requirements.txt
\```

## نقش‌های کاربری

| نقش | دسترسی |
|-----|---------|
| مدیر | همه بخش‌ها |
| منشی | نوبت‌دهی و مشتریان |
| کارکن | نوبت‌های خودش |
| مشتری | رزرو و تاریخچه نوبت‌ها |
