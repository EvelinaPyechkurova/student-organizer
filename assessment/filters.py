from .models import Assessment
from subject.models import Subject
from lesson.models import Lesson

from utils.filter_building_blocks import subject_filter, lesson_filter, timeframe_filter
from utils.filters import generate_select_options

def build_assessment_filters(user): 
    return {
        'subject': subject_filter(subject_model=Subject),
        'lesson': lesson_filter(lesson_model=Lesson, label='Assessment Lesson'),
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
