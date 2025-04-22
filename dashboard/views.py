from django.shortcuts import render
from django.views import View


class DashboardView(View):
    template_name = 'dashboard.html'

    def get(self, request):
        user = request.user
        context = { 
            'context': {
                'username': ('Username', user.username),
                'first_name': ('Name', user.first_name),
                'last_name': ('Lastname', user.last_name),
                'lesson_reminders': ('Recieve lesson remainders', user.userprofile.recieve_lesson_remainders),
                'lesson_reminder_timing': ('Lesson remainder timing', user.userprofile.lesson_remainder_timing),
                'assessment_reminders': ('Recieve assessment remainders', user.userprofile.recieve_assessment_remainders),
                'assessment_reminder_timing': ('Assessment remainder timing', user.userprofile.assessment_remainder_timing),
                'homework_reminders': ('Recieve homework remainders', user.userprofile.recieve_homework_remainders),
                'homework_reminder_timing': ('Homework remainder timing', user.userprofile.homework_remainder_timing),
            }
        }
        return render(request, self.template_name, context)