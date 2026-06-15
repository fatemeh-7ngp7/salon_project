from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


class DashboardIndexView(LoginRequiredMixin, View):
    """ریدایرکت به پنل مناسب بر اساس نقش کاربر"""

    def get(self, request):
        role = request.user.role
        if role == 'owner':
            return redirect('dashboard:owner:index')
        elif role == 'receptionist':
            return redirect('dashboard:receptionist:index')
        elif role == 'staff':
            return redirect('dashboard:staff:index')
        else:
            return redirect('dashboard:customer:index')