from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('شماره موبایل الزامی است')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.OWNER)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        OWNER = 'owner', 'صاحب سالن'
        RECEPTIONIST = 'receptionist', 'منشی'
        STAFF = 'staff', 'کارکن'
        CUSTOMER = 'customer', 'مشتری'

    # فیلدهای اصلی
    phone = models.CharField(
        max_length=11,
        unique=True,
        verbose_name='شماره موبایل'
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name='نام'
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name='نام خانوادگی'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='ایمیل'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        verbose_name='نقش'
    )

    work_note = models.TextField(
        blank=True,
        verbose_name='یادداشت برنامه کاری',
        help_text='برنامه کاری هفتگی منشی'
    )

    # فیلدهای سیستمی
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_staff = models.BooleanField(default=False, verbose_name='دسترسی ادمین')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='تاریخ عضویت')
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name='ثبت شده توسط'
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    # helper properties برای چک کردن نقش
    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST

    @property
    def is_staff_member(self):
        return self.role == self.Role.STAFF

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER