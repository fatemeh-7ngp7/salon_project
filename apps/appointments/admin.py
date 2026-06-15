from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'customer', 'staff', 'service',
        'date', 'start_time', 'end_time',
        'status', 'booked_by', 'created_at'
    ]
    list_filter = ['status', 'date', 'staff']
    search_fields = [
        'customer__first_name', 'customer__last_name',
        'customer__phone'
    ]
    readonly_fields = ['end_time', 'created_at', 'updated_at']
    ordering = ['-date', '-start_time']