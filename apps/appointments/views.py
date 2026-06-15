from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.staff.models import StaffProfile
from apps.services.models import Service
from .utils import get_available_slots
import datetime


class GetStaffServicesView(LoginRequiredMixin, View):
    def get(self, request, staff_id):
        try:
            staff = StaffProfile.objects.get(pk=staff_id, is_active=True)
            services = staff.staff_services.filter(
                is_active=True
            ).select_related('service')

            data = [{
                'id': ss.service.pk,
                'name': ss.service.name,
                'duration': ss.service.duration,
                'duration_display': ss.service.duration_display,
                'price': str(ss.service.price),
            } for ss in services]

            return JsonResponse({'services': data})
        except StaffProfile.DoesNotExist:
            return JsonResponse({'services': []})


class GetAvailableSlotsView(LoginRequiredMixin, View):
    def get(self, request):
        staff_id = request.GET.get('staff_id')
        service_id = request.GET.get('service_id')
        date_str = request.GET.get('date')
        customer_id = request.GET.get('customer_id')

        if not all([staff_id, service_id, date_str]):
            return JsonResponse({'slots': [], 'error': 'اطلاعات ناقص است'})

        try:
            from apps.accounts.models import User
            staff = StaffProfile.objects.get(pk=staff_id, is_active=True)
            service = Service.objects.get(pk=service_id, is_active=True)
            date = datetime.date.fromisoformat(date_str)

            if date < datetime.date.today():
                return JsonResponse({'slots': [], 'error': 'تاریخ انتخابی گذشته است'})

            # تعیین مشتری برای چک تداخل
            current_customer = None
            if customer_id:
                try:
                    current_customer = User.objects.get(pk=customer_id, role='customer')
                except User.DoesNotExist:
                    pass
            elif request.user.role == 'customer':
                current_customer = request.user

            slots = get_available_slots(staff, service, date, current_customer)
            return JsonResponse({'slots': slots})

        except Exception as e:
            return JsonResponse({'slots': [], 'error': str(e)})


class GetStaffWorkDaysView(LoginRequiredMixin, View):
    """API: روزهای کاری یک کارکن"""

    def get(self, request, staff_id):
        try:
            staff = StaffProfile.objects.get(pk=staff_id, is_active=True)
            schedules = staff.work_schedules.filter(is_available=True)

            # تبدیل روزهای ایرانی به اعداد weekday پایتون
            iranian_to_python = {
                0: 5,  # شنبه → Saturday
                1: 6,  # یکشنبه → Sunday
                2: 0,  # دوشنبه → Monday
                3: 1,  # سه‌شنبه → Tuesday
                4: 2,  # چهارشنبه → Wednesday
                5: 3,  # پنجشنبه → Thursday
                6: 4,  # جمعه → Friday
            }

            work_days = [iranian_to_python[s.day_of_week] for s in schedules]

            return JsonResponse({
                'work_days': work_days,
                'schedules': [{
                    'day': s.get_day_of_week_display(),
                    'start': s.start_time.strftime('%H:%M'),
                    'end': s.end_time.strftime('%H:%M'),
                } for s in schedules]
            })
        except StaffProfile.DoesNotExist:
            return JsonResponse({'work_days': [], 'schedules': []})