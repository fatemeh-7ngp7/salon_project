from django.db import models
from django.conf import settings
from apps.services.models import ServiceCategory, Service


class StaffProfile(models.Model):
    """پروفایل کارکنان سالن"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile',
        verbose_name='کاربر'
    )
    specialty = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name='staff_members',
        verbose_name='تخصص'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='بیوگرافی'
    )
    profile_image = models.ImageField(
        upload_to='staff/images/',
        blank=True,
        null=True,
        verbose_name='تصویر پروفایل'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ عضویت'
    )

    class Meta:
        verbose_name = 'پروفایل کارکن'
        verbose_name_plural = 'پروفایل کارکنان'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialty.name}"


class StaffService(models.Model):
    """کدام کارکن کدام خدمت را ارائه می‌دهد"""

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name='staff_services',
        verbose_name='کارکن'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='staff_services',
        verbose_name='خدمت'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )

    class Meta:
        verbose_name = 'خدمت کارکن'
        verbose_name_plural = 'خدمات کارکنان'
        unique_together = ['staff', 'service']

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.service.name}"

    def clean(self):
        """بررسی که خدمت انتخابی در حوزه تخصص کارکن باشد"""
        from django.core.exceptions import ValidationError
        if self.service.category != self.staff.specialty:
            raise ValidationError(
                f'خدمت {self.service.name} در حوزه تخصص این کارکن نیست.'
            )


class WorkSchedule(models.Model):
    """برنامه کاری کارکنان"""

    class DayOfWeek(models.IntegerChoices):
        SATURDAY = 0, 'شنبه'
        SUNDAY = 1, 'یکشنبه'
        MONDAY = 2, 'دوشنبه'
        TUESDAY = 3, 'سه‌شنبه'
        WEDNESDAY = 4, 'چهارشنبه'
        THURSDAY = 5, 'پنجشنبه'
        FRIDAY = 6, 'جمعه'

    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name='work_schedules',
        verbose_name='کارکن'
    )
    day_of_week = models.IntegerField(
        choices=DayOfWeek.choices,
        verbose_name='روز هفته'
    )
    start_time = models.TimeField(
        verbose_name='شروع کار'
    )
    end_time = models.TimeField(
        verbose_name='پایان کار'
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name='در دسترس'
    )

    class Meta:
        verbose_name = 'برنامه کاری'
        verbose_name_plural = 'برنامه‌های کاری'
        unique_together = ['staff', 'day_of_week']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.get_day_of_week_display()}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError('ساعت شروع باید قبل از ساعت پایان باشد.')