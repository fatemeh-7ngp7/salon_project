from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardIndexView.as_view(), name='index'),

    # مدیر
    path('owner/', include('apps.dashboard.urls_owner', namespace='owner')),

    # منشی
    path('receptionist/', include('apps.dashboard.urls_receptionist', namespace='receptionist')),

    # کارکن
    path('staff/', include('apps.dashboard.urls_staff', namespace='staff')),

    # مشتری
    path('customer/', include('apps.dashboard.urls_customer', namespace='customer')),
]