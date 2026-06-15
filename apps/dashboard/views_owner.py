from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from apps.accounts.mixins import OwnerRequiredMixin
from apps.accounts.models import User
from apps.services.models import ServiceCategory, Service
from apps.staff.models import StaffProfile, WorkSchedule, StaffService
from apps.appointments.models import Appointment
import re


class OwnerDashboardView(OwnerRequiredMixin, View):
    def get(self, request):
        context = {
            'total_staff': StaffProfile.objects.filter(is_active=True).count(),
            'total_customers': User.objects.filter(role='customer').count(),
            'today_appointments': Appointment.objects.filter(
                status__in=['pending', 'confirmed']
            ).count(),
            'total_services': Service.objects.filter(is_active=True).count(),
        }
        return render(request, 'dashboard/admin/index.html', context)


class UserListView(OwnerRequiredMixin, View):
    def get(self, request):
        users = User.objects.exclude(role='owner').order_by('role', '-date_joined')
        return render(request, 'dashboard/admin/user_list.html', {'users': users})


class UserCreateView(OwnerRequiredMixin, View):
    def get(self, request):
        return render(request, 'dashboard/admin/user_form.html')

    def post(self, request):
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', 'customer')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []

        if not all([first_name, last_name, phone]):
            errors.append('نام، نام خانوادگی و شماره موبایل الزامی است.')

        if not re.match(r'^09[0-9]{9}$', phone):
            errors.append('شماره موبایل معتبر نیست.')

        if User.objects.filter(phone=phone).exists():
            errors.append('این شماره موبایل قبلاً ثبت شده است.')

        if password1 != password2:
            errors.append('رمز عبور و تکرار آن یکسان نیستند.')

        if len(password1) < 8:
            errors.append('رمز عبور باید حداقل ۸ کاراکتر باشد.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'dashboard/admin/user_form.html',
                         {'form_data': request.POST})

        user = User.objects.create_user(
            phone=phone,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            email=email or None,
            role=role,
            created_by=request.user
        )
        messages.success(request, f'کاربر {user.get_full_name()} با موفقیت ایجاد شد.')
        return redirect('dashboard:owner:user_list')


class UserEditView(OwnerRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return render(request, 'dashboard/admin/user_form.html', {'user': user})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', user.role)
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not all([first_name, last_name, phone]):
            messages.error(request, 'نام، نام خانوادگی و شماره موبایل الزامی است.')
            return render(request, 'dashboard/admin/user_form.html', {'user': user})

        if not re.match(r'^09[0-9]{9}$', phone):
            messages.error(request, 'شماره موبایل معتبر نیست.')
            return render(request, 'dashboard/admin/user_form.html', {'user': user})

            # چک تکراری نبودن شماره (به جز خود کاربر)
        if User.objects.filter(phone=phone).exclude(pk=pk).exists():
            messages.error(request, 'این شماره موبایل قبلاً ثبت شده است.')
            return render(request, 'dashboard/admin/user_form.html', {'user': user})

        # جلوگیری از تغییر نقش owner
        if user.role == 'owner':
            messages.error(request, 'نقش صاحب سالن قابل تغییر نیست.')
            return redirect('dashboard:owner:user_list')

        # تغییر رمز عبور اگه وارد شده
        if password1:
            if password1 != password2:
                messages.error(request, 'رمز عبور و تکرار آن یکسان نیستند.')
                return render(request, 'dashboard/admin/user_form.html', {'user': user})
            if len(password1) < 8:
                messages.error(request, 'رمز عبور باید حداقل ۸ کاراکتر باشد.')
                return render(request, 'dashboard/admin/user_form.html', {'user': user})
            user.set_password(password1)

        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.email = email or None
        user.role = role
        user.save()

        messages.success(request, f'اطلاعات {user.get_full_name()} بروزرسانی شد.')
        return redirect('dashboard:owner:user_list')


class UserToggleActiveView(OwnerRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        status = 'فعال' if user.is_active else 'غیرفعال'
        messages.success(request, f'کاربر {user.get_full_name()} {status} شد.')
        return redirect('dashboard:owner:user_list')


class CategoryListView(OwnerRequiredMixin, View):
    def get(self, request):
        categories = ServiceCategory.objects.all()
        return render(request, 'dashboard/admin/category_list.html',
                     {'categories': categories})


class CategoryCreateView(OwnerRequiredMixin, View):
    def get(self, request):
        return render(request, 'dashboard/admin/category_form.html')

    def post(self, request):
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, 'نام دسته‌بندی الزامی است.')
            return render(request, 'dashboard/admin/category_form.html')

        if ServiceCategory.objects.filter(name=name).exists():
            messages.error(request, 'این دسته‌بندی قبلاً ثبت شده است.')
            return render(request, 'dashboard/admin/category_form.html')

        ServiceCategory.objects.create(
            name=name,
            icon=icon,
            description=description
        )
        messages.success(request, f'دسته‌بندی "{name}" با موفقیت ایجاد شد.')
        return redirect('dashboard:owner:category_list')


class ServiceListView(OwnerRequiredMixin, View):
    def get(self, request):
        services = Service.objects.select_related('category').all()
        return render(request, 'dashboard/admin/service_list.html',
                     {'services': services})


class ServiceCreateView(OwnerRequiredMixin, View):
    def get(self, request):
        categories = ServiceCategory.objects.filter(is_active=True)
        return render(request, 'dashboard/admin/service_form.html',
                     {'categories': categories})

    def post(self, request):
        category_id = request.POST.get('category')
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        duration = request.POST.get('duration')
        price = request.POST.get('price')

        categories = ServiceCategory.objects.filter(is_active=True)
        errors = []

        if not all([category_id, name, duration, price]):
            errors.append('همه فیلدهای ضروری را پر کنید.')

        try:
            duration = int(duration)
            if duration < 15:
                errors.append('مدت زمان باید حداقل ۱۵ دقیقه باشد.')
        except (ValueError, TypeError):
            errors.append('مدت زمان معتبر نیست.')

        try:
            price = int(price)
        except (ValueError, TypeError):
            errors.append('قیمت معتبر نیست.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'dashboard/admin/service_form.html',
                         {'categories': categories})

        category = get_object_or_404(ServiceCategory, pk=category_id)
        Service.objects.create(
            category=category,
            name=name,
            description=description,
            duration=duration,
            price=price
        )
        messages.success(request, f'خدمت "{name}" با موفقیت ایجاد شد.')
        return redirect('dashboard:owner:service_list')


class ServiceEditView(OwnerRequiredMixin, View):
    def get(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        categories = ServiceCategory.objects.filter(is_active=True)
        return render(request, 'dashboard/admin/service_form.html', {
            'service': service,
            'categories': categories
        })

    def post(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        categories = ServiceCategory.objects.filter(is_active=True)

        category_id = request.POST.get('category')
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        duration = request.POST.get('duration')
        price = request.POST.get('price')

        try:
            duration = int(duration)
            price = int(price)
        except (ValueError, TypeError):
            messages.error(request, 'مقادیر عددی معتبر نیستند.')
            return render(request, 'dashboard/admin/service_form.html', {
                'service': service, 'categories': categories
            })

        category = get_object_or_404(ServiceCategory, pk=category_id)
        service.category = category
        service.name = name
        service.description = description
        service.duration = duration
        service.price = price
        service.save()

        messages.success(request, f'خدمت "{name}" بروزرسانی شد.')
        return redirect('dashboard:owner:service_list')

class ReceptionistScheduleView(OwnerRequiredMixin, View):
    def get(self, request, pk):
        receptionist = get_object_or_404(User, pk=pk, role='receptionist')
        return render(request, 'dashboard/admin/receptionist_schedule.html', {
            'receptionist': receptionist,
        })

    def post(self, request, pk):
        receptionist = get_object_or_404(User, pk=pk, role='receptionist')
        work_note = request.POST.get('work_note', '').strip()
        receptionist.work_note = work_note
        receptionist.save()
        messages.success(request, 'برنامه کاری منشی ذخیره شد.')
        return redirect('dashboard:owner:receptionist_schedule', pk=pk)


class StaffListView(OwnerRequiredMixin, View):
    def get(self, request):
        staff = StaffProfile.objects.select_related(
            'user', 'specialty'
        ).all()
        receptionists = User.objects.filter(role='receptionist')

        # کاربران staff که هنوز پروفایل ندارن
        existing_staff_user_ids = StaffProfile.objects.values_list('user_id', flat=True)
        pending_staff = User.objects.filter(
            role='staff'
        ).exclude(id__in=existing_staff_user_ids)

        return render(request, 'dashboard/admin/staff_list.html', {
            'staff': staff,
            'receptionists': receptionists,
            'pending_staff': pending_staff,
        })

class StaffCreateView(OwnerRequiredMixin, View):
    def get(self, request):
        categories = ServiceCategory.objects.filter(is_active=True)
        # اگه user_id از قبل داده شده (از لیست pending)
        preselected_user = None
        user_id = request.GET.get('user_id')
        if user_id:
            preselected_user = User.objects.filter(pk=user_id, role='staff').first()

        return render(request, 'dashboard/admin/staff_form.html', {
            'categories': categories,
            'preselected_user': preselected_user,
        })

    def post(self, request):
        categories = ServiceCategory.objects.filter(is_active=True)

        # چک کن آیا user از قبل وجود داره یا باید جدید بسازیم
        existing_user_id = request.POST.get('existing_user_id')

        if existing_user_id:
            # فقط پروفایل بساز
            user = get_object_or_404(User, pk=existing_user_id, role='staff')
            specialty_id = request.POST.get('specialty')
            bio = request.POST.get('bio', '').strip()

            if not specialty_id:
                messages.error(request, 'تخصص الزامی است.')
                return render(request, 'dashboard/admin/staff_form.html', {
                    'categories': categories,
                    'preselected_user': user,
                })

            specialty = get_object_or_404(ServiceCategory, pk=specialty_id)
            staff = StaffProfile.objects.create(
                user=user,
                specialty=specialty,
                bio=bio
            )
            messages.success(request, f'پروفایل {user.get_full_name()} ایجاد شد.')
            return redirect('dashboard:owner:staff_detail', pk=staff.pk)

        else:
            # کاربر جدید بساز + پروفایل
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')
            specialty_id = request.POST.get('specialty')
            bio = request.POST.get('bio', '').strip()

            errors = []
            if not all([first_name, last_name, phone, password1, specialty_id]):
                errors.append('همه فیلدهای ضروری را پر کنید.')
            if phone and not re.match(r'^09[0-9]{9}$', phone):
                errors.append('شماره موبایل معتبر نیست.')
            if phone and User.objects.filter(phone=phone).exists():
                errors.append('این شماره موبایل قبلاً ثبت شده است.')
            if password1 != password2:
                errors.append('رمز عبور و تکرار آن یکسان نیستند.')
            if password1 and len(password1) < 8:
                errors.append('رمز عبور باید حداقل ۸ کاراکتر باشد.')

            if errors:
                for e in errors:
                    messages.error(request, e)
                return render(request, 'dashboard/admin/staff_form.html', {
                    'categories': categories,
                    'form_data': request.POST,
                })

            user = User.objects.create_user(
                phone=phone,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                email=email or None,
                role='staff',
                created_by=request.user
            )
            specialty = get_object_or_404(ServiceCategory, pk=specialty_id)
            staff = StaffProfile.objects.create(
                user=user,
                specialty=specialty,
                bio=bio
            )
            messages.success(request, f'کارکن {user.get_full_name()} با موفقیت ایجاد شد.')
            return redirect('dashboard:owner:staff_detail', pk=staff.pk)

class StaffDetailView(OwnerRequiredMixin, View):
    def get(self, request, pk):
        staff = get_object_or_404(StaffProfile, pk=pk)
        # خدماتی که در حوزه تخصص کارکن هست و هنوز اضافه نشده
        existing_services = staff.staff_services.values_list('service_id', flat=True)
        available_services = Service.objects.filter(
            category=staff.specialty,
            is_active=True
        ).exclude(id__in=existing_services)

        return render(request, 'dashboard/admin/staff_detail.html', {
            'staff': staff,
            'available_services': available_services
        })

    def post(self, request, pk):
        staff = get_object_or_404(StaffProfile, pk=pk)
        action = request.POST.get('action')

        if action == 'add_service':
            service_id = request.POST.get('service_id')
            service = get_object_or_404(Service, pk=service_id)
            StaffService.objects.get_or_create(staff=staff, service=service)
            messages.success(request, f'خدمت "{service.name}" اضافه شد.')

        elif action == 'remove_service':
            service_id = request.POST.get('service_id')
            StaffService.objects.filter(staff=staff, service_id=service_id).delete()
            messages.success(request, 'خدمت حذف شد.')

        return redirect('dashboard:owner:staff_detail', pk=pk)


class StaffScheduleView(OwnerRequiredMixin, View):
    def get(self, request, pk):
        staff = get_object_or_404(StaffProfile, pk=pk)
        schedules = staff.work_schedules.all().order_by('day_of_week')
        return render(request, 'dashboard/admin/staff_schedule.html', {
            'staff': staff,
            'schedules': schedules
        })

    def post(self, request, pk):
        staff = get_object_or_404(StaffProfile, pk=pk)
        action = request.POST.get('action')

        if action == 'add_schedule':
            day_of_week = request.POST.get('day_of_week')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            if not all([day_of_week, start_time, end_time]):
                messages.error(request, 'همه فیلدها الزامی است.')
                return redirect('dashboard:owner:staff_schedule', pk=pk)

            if start_time >= end_time:
                messages.error(request, 'ساعت شروع باید قبل از پایان باشد.')
                return redirect('dashboard:owner:staff_schedule', pk=pk)

            WorkSchedule.objects.update_or_create(
                staff=staff,
                day_of_week=int(day_of_week),
                defaults={
                    'start_time': start_time,
                    'end_time': end_time,
                    'is_available': True
                }
            )
            messages.success(request, 'برنامه کاری ذخیره شد.')

        elif action == 'delete_schedule':
            schedule_id = request.POST.get('schedule_id')
            WorkSchedule.objects.filter(pk=schedule_id, staff=staff).delete()
            messages.success(request, 'روز کاری حذف شد.')

        return redirect('dashboard:owner:staff_schedule', pk=pk)


class AppointmentListView(OwnerRequiredMixin, View):
    def get(self, request):
        appointments = Appointment.objects.select_related(
            'customer', 'staff__user', 'service', 'booked_by'
        ).order_by('-date', '-start_time')
        return render(request, 'dashboard/admin/appointment_list.html', {
            'appointments': appointments
        })


class AppointmentDetailView(OwnerRequiredMixin, View):
    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        return render(request, 'dashboard/admin/appointment_detail.html', {
            'appointment': appointment
        })

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        action = request.POST.get('action')

        if action == 'confirm':
            appointment.status = Appointment.Status.CONFIRMED
            appointment.save()
            messages.success(request, 'نوبت تأیید شد.')
        elif action == 'cancel':
            reason = request.POST.get('reason', '')
            appointment.cancel(reason=reason, cancelled_by=request.user)
            messages.success(request, 'نوبت لغو شد.')
        elif action == 'complete':
            appointment.status = Appointment.Status.COMPLETED
            appointment.save()
            messages.success(request, 'نوبت به عنوان انجام شده ثبت شد.')

        return redirect('dashboard:owner:appointment_detail', pk=pk)

class AppointmentCreateView(OwnerRequiredMixin, View):
    def get(self, request):
        from django.utils import timezone
        staff_members = StaffProfile.objects.filter(is_active=True).select_related('user', 'specialty')
        customers = User.objects.filter(role='customer').order_by('first_name')
        return render(request, 'dashboard/admin/appointment_form.html', {
            'staff_members': staff_members,
            'customers': customers,
            'today': timezone.now().date().isoformat(),
        })

    def post(self, request):
        from apps.services.models import Service
        import datetime

        customer_id = request.POST.get('customer')
        staff_id = request.POST.get('staff')
        service_id = request.POST.get('service')
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        notes = request.POST.get('notes', '')

        staff_members = StaffProfile.objects.filter(is_active=True).select_related('user', 'specialty')
        customers = User.objects.filter(role='customer').order_by('first_name')

        if not all([customer_id, staff_id, service_id, date_str, start_time_str]):
            messages.error(request, 'همه فیلدهای ضروری را پر کنید.')
            return render(request, 'dashboard/admin/appointment_form.html', {
                'staff_members': staff_members,
                'customers': customers,
                'today': date_str or '',
            })

        try:
            # تبدیل string به datetime.date و datetime.time
            date_obj = datetime.date.fromisoformat(date_str)
            time_obj = datetime.time.fromisoformat(start_time_str)

            customer = get_object_or_404(User, pk=customer_id)
            staff = get_object_or_404(StaffProfile, pk=staff_id)
            service = get_object_or_404(Service, pk=service_id)

            appointment = Appointment(
                customer=customer,
                staff=staff,
                service=service,
                date=date_obj,
                start_time=time_obj,
                booked_by=request.user,
                notes=notes,
                status=Appointment.Status.CONFIRMED
            )
            appointment.save()
            messages.success(request, 'نوبت با موفقیت ثبت شد.')
            return redirect('dashboard:owner:appointment_list')

        except ValueError as e:
            messages.error(request, f'فرمت تاریخ یا ساعت اشتباه است: {str(e)}')
        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')

        return render(request, 'dashboard/admin/appointment_form.html', {
            'staff_members': staff_members,
            'customers': customers,
            'today': date_str or '',
        })