from django.views.generic import DetailView

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