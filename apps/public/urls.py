from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('staff/<int:pk>/', views.StaffDetailView.as_view(), name='staff_detail'),
]