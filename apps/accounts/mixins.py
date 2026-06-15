from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages


class OwnerRequiredMixin(AccessMixin):
    """فقط صاحب سالن"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'owner':
            messages.error(request, 'شما دسترسی به این صفحه را ندارید.')
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)


class ReceptionistRequiredMixin(AccessMixin):
    """فقط منشی"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'receptionist':
            messages.error(request, 'شما دسترسی به این صفحه را ندارید.')
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)


class StaffRequiredMixin(AccessMixin):
    """فقط کارکن"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'staff':
            messages.error(request, 'شما دسترسی به این صفحه را ندارید.')
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)


class CustomerRequiredMixin(AccessMixin):
    """فقط مشتری"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'customer':
            messages.error(request, 'شما دسترسی به این صفحه را ندارید.')
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)


class OwnerOrReceptionistMixin(AccessMixin):
    """صاحب سالن یا منشی"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in ['owner', 'receptionist']:
            messages.error(request, 'شما دسترسی به این صفحه را ندارید.')
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)


class AnyStaffMixin(AccessMixin):
    """هر کارکن سالن (owner، receptionist، staff)"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in ['owner', 'receptionist', 'staff']:
            messages.error(request, 'شما دسترسی به این صفحه را ندارید.')
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)