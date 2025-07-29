def get_subject(obj):
    '''
    Returns subject object certain event belongs to.
    '''
    if type(obj).__name__ == 'Subject':
        return obj
    elif type(obj).__name__ == 'Lesson':
        return obj.subject
    elif type(obj).__name__ in ('Assessment', 'Homework'):
        return obj.derived_subject
    else:
        raise ValueError(f'Unsupported object type: {type(obj).__name__}')

def get_user(obj):
    '''
    Returns user object certain event belongs to.
    '''
    subject = get_subject(obj)
    return subject.user

def get_userprofile(obj):
    '''
    Return userprofile of a user
    certain event belongs to.
    '''
    user = get_user(obj)
    return user.userprofile
