from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils import timezone
from apps.accounts.mixins import ReceptionistRequiredMixin
from apps.accounts.models import User
from apps.staff.models import StaffProfile, WorkSchedule
from apps.appointments.models import Appointment
import datetime


class ReceptionistDashboardView(ReceptionistRequiredMixin, View):
    def get(self, request):
        today = timezone.now().date()
        context = {
            'today_appointments': Appointment.objects.filter(
                date=today,
                status__in=['pending', 'confirmed']
            ).count(),
            'total_customers': User.objects.filter(role='customer').count(),
        }
        return render(request, 'dashboard/receptionist/index.html', context)


class AppointmentListView(ReceptionistRequiredMixin, View):
    def get(self, request):
        appointments = Appointment.objects.select_related(
            'customer', 'staff__user', 'service', 'booked_by'
        ).order_by('-date', '-start_time')
        return render(request, 'dashboard/receptionist/appointment_list.html', {
            'appointments': appointments
        })


class AppointmentCreateView(ReceptionistRequiredMixin, View):
    def get(self, request):
        staff_members = StaffProfile.objects.filter(
            is_active=True
        ).select_related('user', 'specialty')
        customers = User.objects.filter(role='customer').order_by('first_name')
        # پیش‌انتخاب از query string
        preselected_customer = request.GET.get('customer')
        preselected_staff = request.GET.get('staff')
        return render(request, 'dashboard/receptionist/appointment_form.html', {
            'staff_members': staff_members,
            'customers': customers,
            'today': datetime.date.today().isoformat(),
            'preselected_customer': preselected_customer,
            'preselected_staff': preselected_staff,
        })

    def post(self, request):
        from apps.services.models import Service
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
            return render(request, 'dashboard/receptionist/appointment_form.html', {
                'staff_members': staff_members,
                'customers': customers,
                'today': datetime.date.today().isoformat(),
            })

        try:
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
            messages.success(request, '✅ نوبت با موفقیت ثبت شد.')
            return redirect('dashboard:receptionist:appointment_list')

        except Exception as e:
            messages.error(request, f'خطا در ثبت نوبت: {str(e)}')
            return render(request, 'dashboard/receptionist/appointment_form.html', {
                'staff_members': staff_members,
                'customers': customers,
                'today': datetime.date.today().isoformat(),
            })


class AppointmentDetailView(ReceptionistRequiredMixin, View):
    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        return render(request, 'dashboard/receptionist/appointment_detail.html', {
            'appointment': appointment
        })


class AppointmentCancelView(ReceptionistRequiredMixin, View):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        reason = request.POST.get('reason', '')
        if appointment.is_cancellable:
            appointment.cancel(reason=reason, cancelled_by=request.user)
            messages.success(request, 'نوبت با موفقیت لغو شد.')
        else:
            messages.error(request, 'امکان لغو نوبت وجود ندارد. لغو فقط تا ۲۴ ساعت قبل امکان‌پذیر است.')
        return redirect('dashboard:receptionist:appointment_list')


class StaffScheduleView(ReceptionistRequiredMixin, View):
    def get(self, request):
        staff_members = StaffProfile.objects.filter(
            is_active=True
        ).select_related('user', 'specialty').prefetch_related('work_schedules')
        return render(request, 'dashboard/receptionist/staff_schedule.html', {
            'staff_members': staff_members
        })


class CustomerListView(ReceptionistRequiredMixin, View):
    def get(self, request):
        customers = User.objects.filter(role='customer').order_by('-date_joined')
        return render(request, 'dashboard/receptionist/customer_list.html', {
            'customers': customers
        })


class CustomerCreateView(ReceptionistRequiredMixin, View):
    def get(self, request):
        return render(request, 'dashboard/receptionist/customer_form.html')

    def post(self, request):
        import re
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []
        if not all([first_name, last_name, phone, password1]):
            errors.append('همه فیلدهای ضروری را پر کنید.')
        if phone and not re.match(r'^09[0-9]{9}$', phone):
            errors.append('شماره موبایل معتبر نیست.')
        if phone and User.objects.filter(phone=phone).exists():
            errors.append('این شماره قبلاً ثبت شده است.')
        if password1 != password2:
            errors.append('رمز عبور و تکرار آن یکسان نیستند.')
        if password1 and len(password1) < 8:
            errors.append('رمز عبور باید حداقل ۸ کاراکتر باشد.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'dashboard/receptionist/customer_form.html',
                         {'form_data': request.POST})

        user = User.objects.create_user(
            phone=phone,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            role='customer',
            created_by=request.user
        )
        messages.success(request, f'مشتری {user.get_full_name()} ثبت شد.')
        return redirect('dashboard:receptionist:customer_list')

class MyScheduleView(ReceptionistRequiredMixin, View):
    def get(self, request):
        return render(request, 'dashboard/receptionist/my_schedule.html', {
            'receptionist': request.user
        })