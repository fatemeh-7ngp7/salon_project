from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils import timezone
from apps.accounts.mixins import StaffRequiredMixin
from apps.staff.models import StaffProfile, WorkSchedule
from apps.appointments.models import Appointment
from apps.accounts.models import User
import datetime


class StaffDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        staff = get_object_or_404(StaffProfile, user=request.user)
        today = timezone.now().date()
        context = {
            'staff': staff,
            'today_appointments': Appointment.objects.filter(
                staff=staff,
                date=today,
                status__in=['pending', 'confirmed']
            ).count(),
            'upcoming_appointments': Appointment.objects.filter(
                staff=staff,
                date__gte=today,
                status__in=['pending', 'confirmed']
            ).order_by('date', 'start_time')[:5],
        }
        return render(request, 'dashboard/staff/index.html', context)


class MyScheduleView(StaffRequiredMixin, View):
    def get(self, request):
        staff = get_object_or_404(StaffProfile, user=request.user)
        schedules = staff.work_schedules.filter(
            is_available=True
        ).order_by('day_of_week')
        return render(request, 'dashboard/staff/schedule.html', {
            'staff': staff,
            'schedules': schedules
        })


class MyAppointmentListView(StaffRequiredMixin, View):
    def get(self, request):
        staff = get_object_or_404(StaffProfile, user=request.user)
        appointments = Appointment.objects.filter(
            staff=staff
        ).select_related(
            'customer', 'service', 'booked_by', 'cancelled_by'
        ).order_by('-date', '-start_time')
        return render(request, 'dashboard/staff/appointment_list.html', {
            'appointments': appointments
        })


class AppointmentCreateView(StaffRequiredMixin, View):
    def get(self, request):
        staff = get_object_or_404(StaffProfile, user=request.user)
        services = staff.staff_services.filter(
            is_active=True
        ).select_related('service')
        customers = User.objects.filter(role='customer').order_by('first_name')
        return render(request, 'dashboard/staff/appointment_form.html', {
            'staff': staff,
            'services': services,
            'customers': customers,
            'today': datetime.date.today().isoformat(),
        })

    def post(self, request):
        from apps.services.models import Service
        staff = get_object_or_404(StaffProfile, user=request.user)
        services = staff.staff_services.filter(is_active=True).select_related('service')
        customers = User.objects.filter(role='customer').order_by('first_name')

        customer_id = request.POST.get('customer')
        service_id = request.POST.get('service')
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        notes = request.POST.get('notes', '')

        if not all([customer_id, service_id, date_str, start_time_str]):
            messages.error(request, 'همه فیلدهای ضروری را پر کنید.')
            return render(request, 'dashboard/staff/appointment_form.html', {
                'staff': staff,
                'services': services,
                'customers': customers,
                'today': datetime.date.today().isoformat(),
            })

        try:
            date_obj = datetime.date.fromisoformat(date_str)
            time_obj = datetime.time.fromisoformat(start_time_str)
            customer = get_object_or_404(User, pk=customer_id)
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
            return redirect('dashboard:staff:appointment_list')

        except Exception as e:
            messages.error(request, f'خطا در ثبت نوبت: {str(e)}')
            return render(request, 'dashboard/staff/appointment_form.html', {
                'staff': staff,
                'services': services,
                'customers': customers,
                'today': datetime.date.today().isoformat(),
            })


class AppointmentDetailView(StaffRequiredMixin, View):
    def get(self, request, pk):
        staff = get_object_or_404(StaffProfile, user=request.user)
        appointment = get_object_or_404(Appointment, pk=pk, staff=staff)
        return render(request, 'dashboard/staff/appointment_detail.html', {
            'appointment': appointment
        })