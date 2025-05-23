from django import forms
from django.contrib.auth.mixins import UserPassesTestMixin

class ModelNameMixin:
    '''
    Adds model name to context data for
    convinient creation of reusable templates.
    '''
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model._meta.model_name
        return context
    

class DerivedFieldsMixin:
    '''
    Overrides queryset to contain fields
    that are derived from oher entities in some way.
    '''
    def get_queryset(self):
        if hasattr(self.model.objects, 'with_derived_fields'):
            return self.model.objects.with_derived_fields()
        return super().get_queryset()
    

class ConstantContextMixin:
    constant_name = None
    context_key = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.constant_name or not self.context_key:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define 'constant_name' and 'context_key'"
            )
        
        module = __import__(self.__module__, fromlist=[self.constant_name])
        try:
            constant_value = getattr(module, self.constant_name)
            context[self.context_key] = constant_value
        except AttributeError:
            raise AttributeError(
                f'{self.__class__.__name__} requires a {self.constant_name} constant '
                f'defined in its module {module.__name__}.'
            )
        
        return context
    

class CancelLinkMixin(ConstantContextMixin):
    constant_name = 'CANCEL_LINK'
    context_key = 'cancel_link'
      

class FilterConfigMixin(ConstantContextMixin):
    constant_name = 'VALID_FILTERS'
    context_key = 'valid_filters'
    

class FilterStateMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = __import__(self.__module__, fromlist=['VALID_FILTERS'])
        try:
            get_request = self.request.GET
            VALID_FILTERS = getattr(module, 'VALID_FILTERS')

            context['selected_values'] = {
                field: get_request.get(field, VALID_FILTERS[field].get('default', ''))
                for field in VALID_FILTERS
            }
            return context
        except AttributeError:
            raise AttributeError(
                f'{self.__class__.__name__} requires a VALID_FILTERS and self.request.GET constant '
                f'defined in its module {module.__name__}.'
            )


class OwnershipRequiredMixin(UserPassesTestMixin):
    '''
    Allows access if the object's owner matches the request user.
    '''
    owner_field = 'user'

    def test_func(self):
        obj = self.get_object()
        owner = getattr(obj, self.owner_field, None)
        return owner == self.request.user or owner == self.request.user.id
    

class UserObjectMixin:
    '''
    Adds current user as object for profile views
    '''
    def get_object(self):
        return self.request.user
    

class DateTimeWidgetMixin:
    datetime_fields = ['start_time', 'due_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.datetime_fields:
            if field in self.fields:
                self.fields[field].widget = forms.DateTimeInput(
                    attrs={'type': 'datetime-local'}
                )
