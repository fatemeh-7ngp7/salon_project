from django.urls import path
from apps.dashboard import views_receptionist as views

app_name = 'receptionist'

urlpatterns = [
    path('', views.ReceptionistDashboardView.as_view(), name='index'),
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/create/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<int:pk>/cancel/', views.AppointmentCancelView.as_view(), name='appointment_cancel'),
    path('staff/schedule/', views.StaffScheduleView.as_view(), name='staff_schedule'),
    path('my-schedule/', views.MyScheduleView.as_view(), name='my_schedule'),  # اضافه شد
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/create/', views.CustomerCreateView.as_view(), name='customer_create'),
]