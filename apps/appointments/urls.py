from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('api/staff/<int:staff_id>/services/',
         views.GetStaffServicesView.as_view(),
         name='staff_services'),
    path('api/available-slots/',
         views.GetAvailableSlotsView.as_view(),
         name='available_slots'),
    path('api/staff/<int:staff_id>/work-days/',
         views.GetStaffWorkDaysView.as_view(),
         name='staff_work_days'),
]