from utils.filter_building_blocks import sort_by

def build_lesson_sorting():
    return sort_by(
        default='start_time',
        options=[
            ('start_time', 'Start Time ⭡'),
            ('-start_time', 'Start Time ⭣'),
        ]
    )