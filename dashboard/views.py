from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class DashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard/dashboard.html'

    def get(self, request):
        user = request.user
        context = { 
            'first_name': user.first_name
        }
        print(context)
        return render(request, self.template_name, context)