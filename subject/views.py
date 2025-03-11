from django.views.generic import ListView, DetailView
from .models import Subject

class SubjectListView(ListView):
    model = Subject
    context_object_name = 'user_subjects'

    def get_queryset(self):
        '''
        Return subjects of the user sending request
        filtered by name if provided in the query params.
        '''
        # queryset = Subject.objects.filter(user=self.request.user)
        queryset = Subject.objects.all()

        name_filter = self.request.GET.get('name')
        print(self.request)
        print(self.request.GET)
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