from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from utils.duration import parse_duration
from utils.query_filters import apply_sorting, apply_timeframe_filter_if_valid
from utils.mixins import (
    CancelLinkMixin, ModelNameMixin,
    GeneralStateMixin, FilterConfigMixin,
    SortConfigMixin, OwnershipRequiredMixin,
    DerivedFieldsMixin
)

from subject.models import Subject
from lesson.models import Lesson
from .forms import AssessmentCreateForm, AssessmentUpdateForm
from .models import Assessment

from .filter_config import build_assessment_filters
from .sort_config import build_assessment_sorting

CANCEL_LINK = reverse_lazy('assessment_list')


class AssessmentListView(LoginRequiredMixin, GeneralStateMixin, 
                         SortConfigMixin, FilterConfigMixin,
                         DerivedFieldsMixin, ListView):
    model = Assessment
    context_object_name = 'user_assessments'
    paginate_by = 7

    state_sources = {
        'filter_config': 'selected_filter_values',
        'sort_config': 'selected_sort_values',
    }

    def build_filter_config(self):
        print(self.request.GET.get('user'))
        return build_assessment_filters(self.request.GET.get('user'))
    
    def build_sort_config(self):
        return build_assessment_sorting()

    def get_queryset(self):
        '''
        Return assessments of the user sending requests
        '''
        queryset = super().get_queryset().filter(derived_user_id=self.request.user.id)
        get_request = self.request.GET
        filter_config = self.build_filter_config()
        sort_config = self.build_sort_config()

        if subject_filter := get_request.get('subject'):
            queryset = queryset.filter(derived_subject_id=subject_filter)
        
        if lesson_filter := get_request.get('lesson'):
            queryset = queryset.filter(lesson=lesson_filter)

        if type_filter := get_request.get('type'):
            queryset = queryset.filter(type__iexact=type_filter)

        
        if duration_filter := get_request.get('duration'):
            valid_duration_options = [option[0] for option in filter_config['duration']['options']]
            if duration_filter in valid_duration_options:
                if duration_filter := parse_duration(duration_filter):
                    queryset = queryset.filter(derived_duration=duration_filter)
                
        else:
            if min_duration_filter := parse_duration(get_request.get('min_duration')):
                queryset = queryset.filter(derived_duration__gte=min_duration_filter)

            if max_duration_filter := parse_duration(get_request.get('max_duration')):
                queryset = queryset.filter(derived_duration__lte=max_duration_filter)


        queryset = apply_timeframe_filter_if_valid(
            get_request=get_request,
            queryset=queryset,
            param_name='start_time',
            valid_filters=filter_config,
            model_field_name='derived_start_time',
        )

        queryset = apply_sorting(get_request, queryset, sort_config)

        return queryset


class AssessmentDetailView(LoginRequiredMixin, DerivedFieldsMixin, OwnershipRequiredMixin,
                           ModelNameMixin, DetailView):
    model = Assessment
    owner_field = 'derived_user_id'


class AssessmentCreateView(LoginRequiredMixin, CancelLinkMixin, DerivedFieldsMixin,
                           ModelNameMixin, CreateView):
    model = Assessment
    form_class = AssessmentCreateForm
    owner_field = 'derived_user_id'
    template_name_suffix = '_form_create'
    success_message = 'Assessment created successfully!'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user_id = self.request.user.id

        form.fields['subject'].queryset = Subject.objects.filter(user=user_id)

        form.fields['lesson'].queryset = (
            Lesson.objects.with_derived_fields()
            .filter(derived_user_id=user_id, start_time__gte=now())
        )

        return form

    def get_initial(self):
        initial = super().get_initial()
        lesson_id = self.request.GET.get('lesson')
        subject_id = self.request.GET.get('subject')

        if lesson_id:
            try:
                lesson = Lesson.objects.get(pk=lesson_id)
                initial.update({
                    'subject': lesson.subject,
                    'lesson': lesson_id,
                    'start_time': lesson.start_time,
                    'duration': lesson.duration,
                })
            except Lesson.DoesNotExist:
                pass
            
        elif subject_id:
            initial['subject'] = subject_id

        return initial

    def get_success_url(self):
        return reverse_lazy('assessment_detail', kwargs = {'pk': self.object.pk})


class AssessmentUpdateView(LoginRequiredMixin, OwnershipRequiredMixin, CancelLinkMixin,
                           DerivedFieldsMixin, ModelNameMixin, UpdateView):
    model = Assessment
    form_class = AssessmentUpdateForm
    owner_field = 'derived_user_id'
    template_name_suffix = '_form_update'
    success_message = 'Assessment updated successfully!'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields['lesson'].queryset = Lesson.objects.filter(
            Q(subject=self.object.derived_subject_id) & (
                Q(pk=self.object.lesson_id) | Q(start_time__gte=now())
            )
        )
    
        return form

    def get_success_url(self):
        return reverse_lazy('assessment_detail', kwargs = {'pk': self.object.pk})


class AssessmentDeleteView(LoginRequiredMixin, OwnershipRequiredMixin, CancelLinkMixin,
                         DerivedFieldsMixin, ModelNameMixin, DeleteView):
    model = Assessment
    owner_field = 'derived_user_id'
    success_message = 'Assessment deleted successfully!'
    success_url = reverse_lazy('assessment_list')
