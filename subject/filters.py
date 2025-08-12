from utils.filter_building_blocks import sort_by

def build_subject_filters():
    return {
        'name': {
            'type': 'text',
            'label': 'Name Contains'
        },
        'sort_by': sort_by(
            default='name',
            options=[
                ('name', 'Name ⭡'),
                ('-name', 'Name ⭣'),
            ]
        )
    }
