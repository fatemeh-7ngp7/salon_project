from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils import timezone
from apps.accounts.mixins import CustomerRequiredMixin
from apps.appointments.models import Appointment
from apps.staff.models import StaffProfile
from apps.services.models import Service, ServiceCategory
import datetime


class CustomerDashboardView(CustomerRequiredMixin, View):
    def get(self, request):
        today = timezone.now().date()
        upcoming = Appointment.objects.filter(
            customer=request.user,
            date__gte=today,
            status__in=['pending', 'confirmed']
        ).order_by('date', 'start_time')[:3]
        context = {'upcoming_appointments': upcoming}
        return render(request, 'dashboard/customer/index.html', context)


class AppointmentListView(CustomerRequiredMixin, View):
    def get(self, request):
        appointments = Appointment.objects.filter(
            customer=request.user
        ).select_related(
            'staff__user', 'service', 'booked_by'
        ).order_by('-date', '-start_time')
        return render(request, 'dashboard/customer/appointment_list.html', {
            'appointments': appointments
        })


class AppointmentCreateView(CustomerRequiredMixin, View):
    def get(self, request):
        staff_members = StaffProfile.objects.filter(
            is_active=True
        ).select_related('user', 'specialty')
        categories = ServiceCategory.objects.filter(is_active=True)

        # پیش‌انتخاب کارکن از URL
        preselected_staff = request.GET.get('staff_id')

        return render(request, 'dashboard/customer/appointment_form.html', {
            'staff_members': staff_members,
            'categories': categories,
            'preselected_staff': preselected_staff,
            'today': datetime.date.today().isoformat(),
            'min_date': datetime.date.today().isoformat(),
        })

    def post(self, request):
        staff_id = request.POST.get('staff')
        service_id = request.POST.get('service')
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        notes = request.POST.get('notes', '')

        staff_members = StaffProfile.objects.filter(
            is_active=True
        ).select_related('user', 'specialty')

        errors = []
        if not all([staff_id, service_id, date_str, start_time_str]):
            errors.append('همه فیلدهای ضروری را پر کنید.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'dashboard/customer/appointment_form.html', {
                'staff_members': staff_members,
                'today': date_str or datetime.date.today().isoformat(),
                'min_date': datetime.date.today().isoformat(),
            })

        try:
            date_obj = datetime.date.fromisoformat(date_str)
            time_obj = datetime.time.fromisoformat(start_time_str)

            staff = get_object_or_404(StaffProfile, pk=staff_id, is_active=True)
            service = get_object_or_404(Service, pk=service_id, is_active=True)

            appointment = Appointment(
                customer=request.user,
                staff=staff,
                service=service,
                date=date_obj,
                start_time=time_obj,
                booked_by=request.user,
                notes=notes,
                status=Appointment.Status.PENDING
            )
            appointment.save()
            messages.success(request, '✅ نوبت شما با موفقیت رزرو شد!')
            return redirect('dashboard:customer:appointment_list')

        except Exception as e:
            messages.error(request, f'خطا در ثبت نوبت: {str(e)}')
            return render(request, 'dashboard/customer/appointment_form.html', {
                'staff_members': staff_members,
                'today': date_str or datetime.date.today().isoformat(),
                'min_date': datetime.date.today().isoformat(),
            })


class AppointmentDetailView(CustomerRequiredMixin, View):
    def get(self, request, pk):
        appointment = get_object_or_404(
            Appointment, pk=pk, customer=request.user
        )
        return render(request, 'dashboard/customer/appointment_detail.html', {
            'appointment': appointment
        })


class AppointmentCancelView(CustomerRequiredMixin, View):
    def post(self, request, pk):
        appointment = get_object_or_404(
            Appointment, pk=pk, customer=request.user
        )
        if appointment.is_cancellable:
            appointment.cancel(cancelled_by=request.user)
            messages.success(request, 'نوبت با موفقیت لغو شد.')
        else:
            messages.error(request, 'امکان لغو نوبت وجود ندارد. لغو نوبت فقط تا ۲۴ ساعت قبل از زمان رزرو امکان‌پذیر است.')
        return redirect('dashboard:customer:appointment_list')


class ProfileView(CustomerRequiredMixin, View):
    def get(self, request):
        appointments_count = Appointment.objects.filter(
            customer=request.user
        ).count()
        return render(request, 'dashboard/customer/profile.html', {
            'appointments_count': appointments_count
        })