from django.contrib import admin
from .models import StaffProfile, StaffService, WorkSchedule


class StaffServiceInline(admin.TabularInline):
    model = StaffService
    extra = 1


class WorkScheduleInline(admin.TabularInline):
    model = WorkSchedule
    extra = 1


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialty', 'is_active', 'created_at']
    list_filter = ['specialty', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'user__phone']
    inlines = [StaffServiceInline, WorkScheduleInline]


@admin.register(StaffService)
class StaffServiceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'service', 'is_active']
    list_filter = ['is_active']


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['staff', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']