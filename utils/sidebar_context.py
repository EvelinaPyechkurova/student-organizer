class SidebarSectionsMixin:
    '''
    Adds "sidebar_sections" to context.
    Override "build_sidebar_sections()" in the view to return
    [{'heading': str, 'configs': {...}} , ...]. State is added later.
    '''
    sort_context_key = 'sidebar_sections'

    def build_sidebar_sections(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} must define build_sort_config() method'."
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.sort_context_key] = self.build_sidebar_sections()
        return context


class SidebarStateMixin:
    '''
    Adds selected state for filters/sorting based on GET params.
    Falls back to defaults. Requires state_sources mapping.
    '''

    sidebar_context_key = 'sidebar_sections'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sections = context.get(self.sidebar_context_key, [])
        GET = self.request.GET

        for section in sections:
            section_configs = section.get('configs')
            section['state'] = {
                field_name: GET.get(
                    field_name,
                    config.get('default', ''))
                for field_name, config in section_configs.items()
            }

        return context
    
def section(heading, configs):
    return {'heading': heading, 'configs': configs}