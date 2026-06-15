from django.db import models


class ServiceCategory(models.Model):
    """دسته‌بندی خدمات - مثل مو، ناخن، پوست"""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='نام دسته‌بندی'
    )
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='آیکون'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    class Meta:
        verbose_name = 'دسته‌بندی خدمات'
        verbose_name_plural = 'دسته‌بندی‌های خدمات'
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """خدمات - مثل مانیکور، پدیکور، رنگ مو"""

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name='services',
        verbose_name='دسته‌بندی'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='نام خدمت'
    )
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات'
    )
    duration = models.PositiveIntegerField(
        verbose_name='مدت زمان (دقیقه)',
        help_text='مدت زمان انجام خدمت به دقیقه'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='قیمت (تومان)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )

    class Meta:
        verbose_name = 'خدمت'
        verbose_name_plural = 'خدمات'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.category.name}"

    @property
    def duration_display(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours and minutes:
            return f"{hours} ساعت و {minutes} دقیقه"
        elif hours:
            return f"{hours} ساعت"
        return f"{minutes} دقیقه"