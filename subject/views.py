from django.views.generic import ListView, DetailView
from .models import Subject

class SubjectListView(ListView):
    model = Subject
    context_object_name = 'user_subjects'
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        return context

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
    

class SubjectDetailView(DetailView):
    model = Subject