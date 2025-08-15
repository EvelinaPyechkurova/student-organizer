from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from subject.filters import build_subject_filters
from subject.sorting import build_subject_sorting

from utils.filters import apply_sorting
from utils.mixins import (
    CancelLinkMixin, ModelNameMixin,
    GeneralStateMixin, FilterConfigMixin,
    SortConfigMixin, OwnershipRequiredMixin,
)

from .models import Subject
from .forms import SubjectForm


CANCEL_LINK = reverse_lazy('subject_list')


class SubjectListView(LoginRequiredMixin, GeneralStateMixin,
                    SortConfigMixin, FilterConfigMixin, ListView):
    model = Subject
    context_object_name = 'user_subjects'
    paginate_by = 20

    state_sources = {
        'filter_config': 'selected_filter_values',
        'sort_config': 'selected_sort_values',
    }

    def build_filter_config(self):
        return build_subject_filters()
    
    def build_sort_config(self):
        return build_subject_sorting()

    def get_queryset(self):
        '''
        Return subjects of the user sending request
        filtered and sorted if provided in the query params.
        '''
        queryset = Subject.objects.filter(user=self.request.user)
        get_request = self.request.GET

        if name_filter := get_request.get('name'):
            queryset = queryset.filter(name__icontains=name_filter)

        queryset = apply_sorting(get_request, queryset, self.build_sort_config())

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