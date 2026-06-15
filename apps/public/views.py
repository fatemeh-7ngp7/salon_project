from django.views import View
from django.shortcuts import render, get_object_or_404
from apps.services.models import ServiceCategory, Service
from apps.staff.models import StaffProfile


class HomeView(View):
    template_name = 'public/home.html'

    def get(self, request):
        categories = ServiceCategory.objects.filter(is_active=True)
        staff_members = StaffProfile.objects.filter(
            is_active=True
        ).select_related('user', 'specialty')
        context = {
            'categories': categories,
            'staff_members': staff_members,
        }
        return render(request, self.template_name, context)


class ServicesView(View):
    template_name = 'public/services.html'

    def get(self, request):
        categories = ServiceCategory.objects.filter(
            is_active=True
        ).prefetch_related(
            'services',
            'services__staff_services',
            'services__staff_services__staff__user',
        )
        return render(request, self.template_name, {'categories': categories})


class StaffDetailView(View):
    template_name = 'public/staff_detail.html'

    def get(self, request, pk):
        staff = get_object_or_404(
            StaffProfile,
            pk=pk,
            is_active=True
        )
        services = staff.staff_services.filter(
            is_active=True
        ).select_related('service')
        schedules = staff.work_schedules.filter(
            is_available=True
        ).order_by('day_of_week')
        context = {
            'staff': staff,
            'services': services,
            'schedules': schedules,
        }
        return render(request, self.template_name, context)