class ModelNameMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model._meta.model_name
        return context
    
class DerivedFieldsMixin:
    def get_queryset(self):
        if hasattr(self.model.objects, 'with_derived_fields'):
            return self.model.objects.with_derived_fields()
        return super().get_queryset()
    
class CancelLinkMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = __import__(self.__module__, fromlist=['CANCEL_LINK'])
        try:
            CANCEL_LINK = getattr(module, 'CANCEL_LINK')
            context['cancel_link'] = CANCEL_LINK
        except AttributeError:
            raise AttributeError(
                f'{self.__class__.__name__} requires a CANCEL_LINK constant '
                f'defined in its module {module.__name__}.'
            )
        
        return context
    
class FilterConfigMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = __import__(self.__module__, fromlist=['VALID_FILTERS'])
        try:
            VALID_FILTERS = getattr(module, 'VALID_FILTERS')
            context['valid_filters'] = VALID_FILTERS
        except AttributeError:
            raise AttributeError(
                f'{self.__class__.__name__} requires a VALID_FILTERS constant '
                f'defined in its module {module.__name__}.'
            )
        
        return context
