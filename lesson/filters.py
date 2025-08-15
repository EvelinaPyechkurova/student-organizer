from .models import Lesson
from subject.models import Subject
from utils.filter_building_blocks import subject_filter, timeframe_filter

def build_lesson_filters(user):
    return {
        'subject': subject_filter(SubjectModel=Subject),
        'type': {
            'type': 'select',
            'label': 'Lesson Type',
            'options': Lesson.Type.choices,
        },
        'start_time': timeframe_filter(label='Start Time')
    }