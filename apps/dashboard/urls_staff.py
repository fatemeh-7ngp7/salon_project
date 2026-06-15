from django.urls import path
from apps.dashboard import views_staff as views

app_name = 'staff'

urlpatterns = [
    path('', views.StaffDashboardView.as_view(), name='index'),
    path('schedule/', views.MyScheduleView.as_view(), name='schedule'),
    path('appointments/', views.MyAppointmentListView.as_view(), name='appointment_list'),
    path('appointments/create/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
]