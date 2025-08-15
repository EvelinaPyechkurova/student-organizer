from utils.filter_building_blocks import sort_by

def build_assessment_sorting():
    return sort_by(
        default='start_time',
        options=[
            ('start_time', 'Start Time ⭡', 'derived_start_time'),
            ('-start_time', 'Start Time ⭣', '-derived_start_time'),
        ]
    )
