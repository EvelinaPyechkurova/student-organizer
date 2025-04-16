from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Subject
from .forms import SubjectForm

from utils.mixins import ModelNameMixin, CancelLinkMixin, FilterConfigMixin
from utils.filters import apply_sorting


VALID_FILTERS = {
    'name': {
        'type': 'text',
        'label': 'Name Contains'
    },
    'sort-by': {
        'type': 'select',
        'label': 'Sort By',
        'default': 'name',
        'options': [
            ('name', 'Name ⭡'),
            ('-name', 'Name ⭣'),
            ('created_at', 'Created At ⭡'),
            ('-created_at', 'Created At ⭣')
        ]
    }
}

CANCEL_LINK = reverse_lazy('subject_list')


class SubjectListView(FilterConfigMixin, ListView):
    model = Subject
    context_object_name = 'user_subjects'
    paginate_by = 20

    def get_queryset(self):
        '''
        Return subjects of the user sending request
        filtered and sorted if provided in the query params.
        '''
        # queryset = Subject.objects.filter(user=self.request.user)
        queryset = Subject.objects.all()

        if name_filter := self.request.GET.get('name'):
            queryset = queryset.filter(name__icontains=name_filter)

        queryset = apply_sorting(self.request, queryset, VALID_FILTERS)

        return queryset
    

class SubjectDetailView(ModelNameMixin, DetailView):
    model = Subject


class SubjectCreateView(CancelLinkMixin, ModelNameMixin, CreateView):
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
    

class SubjectUpdateView(CancelLinkMixin, ModelNameMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    success_message = 'Subject updated successfully!'
    template_name_suffix = '_form_update'
    
    def get_success_url(self):
        return reverse_lazy('subject_detail', kwargs = {'pk': self.object.pk})


class SubjectDeleteView(CancelLinkMixin, ModelNameMixin, DeleteView):
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