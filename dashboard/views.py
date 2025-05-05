from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from datetime import date
import calendar


class DashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard/dashboard.html'

    def get(self, request):
        user = request.user
        today = date.today()
        year = today.year
        month = today.month
        month_name = calendar.month_name[month]
        month_calendar = calendar.monthcalendar(year, month)

        context = { 
            'year': year,
            'month': month_name,
            'calendar': month_calendar,
        }

        return render(request, self.template_name, context)