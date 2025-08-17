from utils.filter_building_blocks import sort_by

def build_subject_sorting():
    return sort_by(
        default='name',
        options=[
            ('name', 'Name ⭡'),
            ('-name', 'Name ⭣'),
        ]
    )