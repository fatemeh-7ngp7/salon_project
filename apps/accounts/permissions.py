from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """فقط صاحب سالن"""
    message = 'فقط صاحب سالن به این بخش دسترسی دارد.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'owner'
        )


class IsReceptionist(BasePermission):
    """فقط منشی"""
    message = 'فقط منشی به این بخش دسترسی دارد.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'receptionist'
        )


class IsStaffMember(BasePermission):
    """فقط کارکن"""
    message = 'فقط کارکنان به این بخش دسترسی دارند.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'staff'
        )


class IsCustomer(BasePermission):
    """فقط مشتری"""
    message = 'فقط مشتریان به این بخش دسترسی دارند.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'customer'
        )


class IsOwnerOrReceptionist(BasePermission):
    """صاحب سالن یا منشی"""
    message = 'فقط صاحب سالن یا منشی به این بخش دسترسی دارند.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['owner', 'receptionist']
        )


class IsOwnerOrStaff(BasePermission):
    """صاحب سالن یا کارکن"""
    message = 'دسترسی محدود است.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['owner', 'staff']
        )


class IsAuthenticatedNotCustomer(BasePermission):
    """همه به جز مشتری"""
    message = 'مشتریان به این بخش دسترسی ندارند.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role != 'customer'
        )