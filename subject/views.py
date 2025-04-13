from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Subject
from .forms import SubjectForm

from utils.mixins import ModelNameMixin


CANCEL_LINK = reverse_lazy('subject_list')


class SubjectListView(ListView):
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

        name_filter = self.request.GET.get('name')

        if name_filter:
            queryset = queryset.filter(name__icontains=name_filter)

        default_sort_param = 'name'
        sort_param = self.request.GET.get('sort_by')
        if sort_param and sort_param in ['name', '-name', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_param)
        else:
            queryset = queryset.order_by(default_sort_param)

        return queryset
    

class SubjectDetailView(ModelNameMixin, DetailView):
    model = Subject


class SubjectCreateView(CreateView):
    model = Subject
    form_class = SubjectForm
    success_message = 'Subject created successfully!'
    template_name_suffix = '_create_form'

    def get_form(self):
        form = super().get_form()
        form.instance.user = self.request.user
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_link'] = CANCEL_LINK
        return context
    
    def get_success_url(self):
        return reverse_lazy('subject_detail', kwargs = {'pk': self.object.pk})
    

class SubjectUpdateView(UpdateView):
    model = Subject
    form_class = SubjectForm
    success_message = 'Subject updated successfully!'
    template_name_suffix = '_update_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_link'] = CANCEL_LINK
        return context


class SubjectDeleteView(ModelNameMixin, DeleteView):
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