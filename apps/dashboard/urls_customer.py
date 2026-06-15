from django.urls import path
from apps.dashboard import views_customer as views

app_name = 'customer'

urlpatterns = [
    path('', views.CustomerDashboardView.as_view(), name='index'),
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/create/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<int:pk>/cancel/', views.AppointmentCancelView.as_view(), name='appointment_cancel'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]