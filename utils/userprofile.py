def get_userprofile(obj):
    if type(obj).__name__ == 'Lesson':
        return obj.subject.user.userprofile
    elif type(obj).__name__ in ('Assessment', 'Homework'):
        return obj.derived_subject.user.userprofile
    else:
        raise ValueError(f'Unsupported object type: {type(obj).__name__}')