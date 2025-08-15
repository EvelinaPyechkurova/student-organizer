from subject.models import Subject
from lesson.models import Lesson

from utils.filter_building_blocks import subject_filter, lesson_filter, timeframe_filter

def build_homework_filters(user):
    return {
        'subject': subject_filter(subject_model=Subject),
        'lesson_given': lesson_filter(lesson_model=Lesson, label='Lesson When Given'),
        'lesson_due': lesson_filter(lesson_model=Lesson, label='Lesson Due For'),
        'lesson': lesson_filter(lesson_model=Lesson, label='Lesson (Given or Due)'),
        'completion': {
            'type': 'select',
            'label': 'Completion Percent',
            'options': [
                ('0', '0% (Not Started)'), 
                ('25', '25% (Started)'), 
                ('50', '50% (Halfway Done)'),
                ('75', '75% (Almost Finished)'), 
                ('100', '100% (Completed)'),
            ],
        },
        'min_completion': {
            'type': 'number',
            'label': 'Minimum Completion Percent',
            'attributes': [
                ('min', '0'),
                ('max', '100'),
                ('step', '1'),
                ('placeholder', 'Enter minimum %'),
            ],
        },
        'max_completion': {
            'type': 'number',
            'label': 'Maximum Completion Percent',
            'attributes': [
                ('min', '0'),
                ('max', '100'),
                ('step', '1'),
                ('placeholder', 'Enter maximum %'),
            ],
        },
        'start_time': timeframe_filter(label='Start Time'),
        'due_at': timeframe_filter(label='Due At'),
    }
