from django.urls import path
from apps.dashboard import views_owner as views

app_name = 'owner'

urlpatterns = [
    path('', views.OwnerDashboardView.as_view(), name='index'),

    # مدیریت کاربران
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('users/<int:pk>/toggle/', views.UserToggleActiveView.as_view(), name='user_toggle'),

    # مدیریت خدمات
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/create/', views.ServiceCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/edit/', views.ServiceEditView.as_view(), name='service_edit'),

    # مدیریت دسته‌بندی
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),

    # مدیریت کارکنان
    path('staff/', views.StaffListView.as_view(), name='staff_list'),
    path('staff/create/', views.StaffCreateView.as_view(), name='staff_create'),
    path('staff/<int:pk>/', views.StaffDetailView.as_view(), name='staff_detail'),
    path('staff/<int:pk>/schedule/', views.StaffScheduleView.as_view(), name='staff_schedule'),

    # برنامه منشی - جدید
    path('receptionist/<int:pk>/schedule/', views.ReceptionistScheduleView.as_view(), name='receptionist_schedule'),

    # نوبت‌ها
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/create/', views.AppointmentCreateView.as_view(), name='appointment_create'),
]