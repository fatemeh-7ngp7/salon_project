from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.staff.models import StaffProfile, WorkSchedule
from apps.services.models import Service
import datetime


class Appointment(models.Model):
    """نوبت‌های رزرو شده"""

    class Status(models.TextChoices):
        PENDING = 'pending', 'در انتظار تأیید'
        CONFIRMED = 'confirmed', 'تأیید شده'
        CANCELLED = 'cancelled', 'لغو شده'
        COMPLETED = 'completed', 'انجام شده'
        NO_SHOW = 'no_show', 'غیبت مشتری'

    # اطلاعات اصلی نوبت
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='appointments',
        verbose_name='مشتری'
    )
    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.PROTECT,
        related_name='appointments',
        verbose_name='کارکن'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='appointments',
        verbose_name='خدمت'
    )

    # زمان نوبت
    date = models.DateField(
        verbose_name='تاریخ نوبت'
    )
    start_time = models.TimeField(
        verbose_name='ساعت شروع'
    )
    end_time = models.TimeField(
        verbose_name='ساعت پایان',
        editable=False
    )

    # وضعیت و اطلاعات تکمیلی
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='وضعیت'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='یادداشت'
    )

    # ردیابی - چه کسی این نوبت را ثبت کرده
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='booked_appointments',
        verbose_name='ثبت شده توسط'
    )

    # زمان ثبت
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی'
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ لغو'
    )
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name='دلیل لغو'
    )

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_appointments',
        verbose_name='لغو شده توسط'
    )

    class Meta:
        verbose_name = 'نوبت'
        verbose_name_plural = 'نوبت‌ها'
        ordering = ['date', 'start_time']

    def __str__(self):
        return (
            f"{self.customer.get_full_name()} - "
            f"{self.service.name} - "
            f"{self.date} {self.start_time}"
        )

    def save(self, *args, **kwargs):
        # محاسبه خودکار ساعت پایان بر اساس مدت زمان خدمت
        if self.start_time and self.service_id:
            start_dt = datetime.datetime.combine(
                datetime.date.today(),
                self.start_time
            )
            end_dt = start_dt + datetime.timedelta(
                minutes=self.service.duration
            )
            self.end_time = end_dt.time()
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not all([self.date, self.start_time, self.staff_id, self.service_id]):
            return

        errors = {}

        # بررسی ۱: تاریخ نباید در گذشته باشد (فقط برای نوبت‌های جدید)
        if not self.pk and self.date < timezone.now().date():
            errors['date'] = 'تاریخ نوبت نمی‌تواند در گذشته باشد.'

        # بررسی ۲: خدمت باید در حوزه تخصص کارکن باشد
        if self.service_id and self.staff_id:
            if self.service.category != self.staff.specialty:
                errors['service'] = 'این خدمت در حوزه تخصص کارکن انتخابی نیست.'

        # بررسی ۳: کارکن باید این خدمت را ارائه دهد
            from apps.staff.models import StaffService
            if not StaffService.objects.filter(
                staff=self.staff,
                service=self.service,
                is_active=True
            ).exists():
                errors['service'] = 'کارکن انتخابی این خدمت را ارائه نمی‌دهد.'

        # بررسی ۴: کارکن در آن روز برنامه کاری داشته باشد
        if self.date and self.staff_id:
            day_of_week = self.date.weekday()
            # تبدیل weekday پایتون به سیستم ایرانی
            # پایتون: 0=دوشنبه ... 6=یکشنبه
            # ما: 0=شنبه ... 6=جمعه
            python_to_iranian = {
                0: 2,  # دوشنبه
                1: 3,  # سه‌شنبه
                2: 4,  # چهارشنبه
                3: 5,  # پنجشنبه
                4: 6,  # جمعه
                5: 0,  # شنبه
                6: 1,  # یکشنبه
            }
            iranian_day = python_to_iranian[day_of_week]

            schedule = WorkSchedule.objects.filter(
                staff=self.staff,
                day_of_week=iranian_day,
                is_available=True
            ).first()

            if not schedule:
                errors['date'] = 'کارکن در این روز کار نمی‌کند.'
            else:
                # بررسی ۵: نوبت در بازه کاری کارکن باشد
                if self.start_time and self.service_id:
                    start_dt = datetime.datetime.combine(
                        datetime.date.today(),
                        self.start_time
                    )
                    end_dt = start_dt + datetime.timedelta(
                        minutes=self.service.duration
                    )
                    end_time = end_dt.time()

                    if self.start_time < schedule.start_time:
                        errors['start_time'] = 'ساعت نوبت قبل از شروع کار کارکن است.'
                    elif end_time > schedule.end_time:
                        errors['start_time'] = 'نوبت بعد از پایان کار کارکن تمام می‌شود.'

        # بررسی ۶: تداخل با نوبت‌های دیگر (double booking)
        if self.date and self.start_time and self.staff_id and self.service_id:
            start_dt = datetime.datetime.combine(
                datetime.date.today(),
                self.start_time
            )
            end_dt = start_dt + datetime.timedelta(
                minutes=self.service.duration
            )
            end_time = end_dt.time()

            overlapping = Appointment.objects.filter(
                staff=self.staff,
                date=self.date,
                status__in=[
                    self.Status.PENDING,
                    self.Status.CONFIRMED
                ]
            ).exclude(pk=self.pk)

            for apt in overlapping:
                # بررسی تداخل زمانی
                if not (end_time <= apt.start_time or
                        self.start_time >= apt.end_time):
                    # اگه همون مشتری هست - مجاز است (چند خدمت متوالی)
                    if apt.customer == self.customer:
                        # ولی نباید دقیقاً همون بازه باشه
                        if self.start_time == apt.start_time:
                            errors['start_time'] = (
                                f'شما قبلاً در این زمان نوبت دارید.'
                            )
                            break
                        # نوبت‌های متوالی یک مشتری مجازند
                        continue
                    else:
                        # مشتری متفاوت - تداخل غیرمجاز
                        errors['start_time'] = (
                            f'این زمان با نوبت '
                            f'{apt.start_time.strftime("%H:%M")} - '
                            f'{apt.end_time.strftime("%H:%M")} '
                            f'تداخل دارد.'
                        )
                        break

        if errors:
            raise ValidationError(errors)

    @property
    def is_cancellable(self):
        """آیا نوبت قابل لغو است - فقط تا ۲۴ ساعت قبل"""
        if self.status in [self.Status.CANCELLED, self.Status.COMPLETED]:
            return False
        appointment_datetime = datetime.datetime.combine(self.date, self.start_time)
        appointment_datetime = timezone.make_aware(appointment_datetime)
        # باید حداقل ۲۴ ساعت مانده باشد
        return appointment_datetime > timezone.now() + datetime.timedelta(hours=24)

    def cancel(self, reason='', cancelled_by=None):
        """لغو نوبت"""
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        if cancelled_by:
            self.cancelled_by = cancelled_by
        self.save()