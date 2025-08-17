from utils.filter_building_blocks import sort_by

def build_homework_sorting():
    return sort_by(
        default='start_time',
        options=[
            ('start_time', 'Start Time ⭡', 'derived_start_time'),
            ('-start_time', 'Start Time ⭣', '-derived_start_time'),
            ('completion', 'Completion Percent ⭡', 'completion_percent'),
            ('-completion', 'Completion Percent ⭣', '-completion_percent'),
        ],
    )