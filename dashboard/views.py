from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from lesson.models import Lesson
from assessment.models import Assessment
from homework.models import Homework

from utils.query_filters import filter_by_day

from datetime import date, timedelta
import calendar


class DashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard/dashboard.html'

    def get(self, request):
        user = self.request.user
        today = date.today()
        year = today.year
        month = today.month
        month_name = calendar.month_name[month]
        month_calendar = calendar.monthcalendar(year, month)

        calendar_events = get_calendar_events(user, get_month_days(year, month))

        context = { 
            'year': year,
            'month': month_name,
            'calendar': month_calendar,
            'calendar_events': calendar_events,
        }

        return render(request, self.template_name, context)
    

def get_month_days(year, month):
    '''
    Returns a list of all days in the specified month as date objects.
    '''
    start_of_month = date(year, month, 1)
    num_days = calendar.monthrange(year, month)[-1]
    return [start_of_month + timedelta(days=n) for n in range(num_days)]


def get_calendar_events(user, month_days):
    '''
    Returns a list off all lessons, assessments and homeworks
    user has in one month along with their dates
    '''
    lessons = Lesson.objects.filter(subject__user=user)
    assessments = Assessment.objects.with_derived_fields().filter(derived_user_id=user.id)
    homeworks = Homework.objects.with_derived_fields().filter(derived_user_id=user.id)
    
    calendar_events = {}

    for day in month_days:
        day_lessons = filter_by_day(lessons, day)
        day_assessments = filter_by_day(assessments, day, date_field='derived_start_time')
        day_homeworks = filter_by_day(homeworks, day, date_field='derived_due_at')

        events = combine_and_sort_by_time(day_lessons, day_assessments, day_homeworks)
        if events:
            calendar_events[day.day] = events

    return calendar_events


def combine_and_sort_by_time(lessons, assessments, homeworks):
    '''
    Combines and sorts assessments, lessons, and homework items
    by their datetime field.
    '''

    event_date = []

    event_date += [('lesson', lesson.id, f'{lesson.subject} {lesson.get_type_display()}', lesson.start_time)
                   for lesson in lessons]
    event_date += [('assessment', assessment.id, f'{assessment.derived_subject} {assessment.get_type_display()}', assessment.derived_start_time)
                   for assessment in assessments]
    event_date += [('homework', homework.id, f'{homework.derived_subject} Homework', homework.derived_due_at)
                   for homework in homeworks]

    sorted_events = sorted(event_date, key=lambda x: x[-1])
    return [(type, pk, description) for type, pk, description, _ in sorted_events]