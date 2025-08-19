from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from utils.mixins import (
    CancelLinkMixin, ModelNameMixin, 
    OwnershipRequiredMixin,
)
from utils.query_filters import apply_sorting
from utils.sidebar_context import (
    SidebarSectionsMixin, SidebarStateMixin,
    section
)

from .models import Subject
from .forms import SubjectForm

from .filter_config import build_subject_filters
from .sort_config import build_subject_sorting


CANCEL_LINK = reverse_lazy('subject_list')


class SubjectListView(LoginRequiredMixin, SidebarStateMixin,
                      SidebarSectionsMixin, ListView):
    model = Subject
    context_object_name = 'user_subjects'
    paginate_by = 20

    def build_sidebar_sections(self):
        return [
            section(heading='Filter By', configs=build_subject_filters()),
            section(heading='Sort By', configs=build_subject_sorting())
        ]

    def get_queryset(self):
        '''
        Return subjects of the user sending request
        filtered and sorted if provided in the query params.
        '''
        queryset = Subject.objects.filter(user=self.request.user)
        GET = self.request.GET

        if name_filter := GET.get('name'):
            queryset = queryset.filter(name__icontains=name_filter)

        queryset = apply_sorting(GET, queryset, build_subject_sorting())

        return queryset
    

class SubjectDetailView(LoginRequiredMixin, OwnershipRequiredMixin, ModelNameMixin,
                        DetailView):
    model = Subject


class SubjectCreateView(LoginRequiredMixin, CancelLinkMixin,
                        ModelNameMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    success_message = 'Subject created successfully!'
    template_name_suffix = '_form_create'

    def get_form(self):
        form = super().get_form()
        form.instance.user = self.request.user
        return form
    
    def get_success_url(self):
        return reverse_lazy('subject_detail', kwargs = {'pk': self.object.pk})
    

class SubjectUpdateView(LoginRequiredMixin, OwnershipRequiredMixin, CancelLinkMixin,
                        ModelNameMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    success_message = 'Subject updated successfully!'
    template_name_suffix = '_form_update'
    
    def get_success_url(self):
        return reverse_lazy('subject_detail', kwargs = {'pk': self.object.pk})


class SubjectDeleteView(LoginRequiredMixin, OwnershipRequiredMixin, CancelLinkMixin,
                        ModelNameMixin, DeleteView):
    model = Subject
    success_message = 'Subject deleted successfully!'
    success_url = reverse_lazy('subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self.object

        lesson_count = subject.lesson_set.count()

        assessment_count = sum(
            (lesson.assessment_set.count() for lesson in subject.lesson_set.all()), 
            subject.assessment_set.count()
        )

        homework_count = sum(
            (lesson.given_homework.count() + lesson.due_homework.count() for lesson in subject.lesson_set.all()),
            subject.homework_set.count()
        )

        if related_objects := {
            key: value for (key, value) in [
                ('lesson', lesson_count),
                ('assessment', assessment_count),
                ('homework', homework_count)
            ]
            if value
        }:
            context['related_objects'] = related_objects

        return context