from .models import Assessment

from utils.filter_building_blocks import subject_filter, lesson_filter, timeframe_filter

def build_assessment_filters(user): 
    return {
        'subject': subject_filter(user),
        'lesson': lesson_filter(user, label='Assessment Lesson'),
        'type': {
            'type': 'select',
            'label': 'Assessment Type',
            'options': Assessment.Type.choices,
        },
        'duration': {
            'type': 'select',
            'label': 'Duration',
            'options': [
                ('15', '15 Minutes'),
                ('30', '30 Minutes'),
                ('45', '45 Minutes'),
                ('60', '1 Hour'),
                ('90', '1 Hour 30 Minutes'),
                ('120', '2 Hours'),
            ],
        },
        'min_duration': {
            'type': 'number',
            'label': 'Minimum Duration',
            'attributes': [
                ('min', '1'),
                ('placeholder', 'Minutes (e.g., 15)'),
            ],
        },
        'max_duration': {
            'type': 'number',
            'label': 'Maximum Duration',
            'attributes': [
                ('min', '1'),
                ('placeholder', 'Minutes (e.g., 90)'),
            ],
        },
        'start_time': timeframe_filter(label='Start Time'),
    }
