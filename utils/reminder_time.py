USER_REMINDER_FIELD_SUFFIX = '_reminder_timing'

def get_reminder_timing_from_user_profile(userprofile, event_type: str):
    '''
    Returns reminder timing for the given event type
    (lesson, assessment, homework) from the user's profile.
    '''
    try:
        return getattr(userprofile, f'{event_type}{USER_REMINDER_FIELD_SUFFIX}')
    except AttributeError as e:
        raise AttributeError(f'UserProfile has no reminder timing for event type "{event_type}".')



def calculate_scheduled_reminder_time(instance, userprofile, event_type: str):
    '''
    Calculates the exact datetime when the reminder should be sent,
    based on user preferences and the event's start or due time.
    '''
    reminder_timing = get_reminder_timing_from_user_profile(userprofile, event_type)

    if event_type in ('lesson', 'assessment'):
        return instance.start_time - reminder_timing
    elif event_type == 'homework':
        return instance.due_at - reminder_timing
    else:
        raise ValueError(f"Unknown event type: '{event_type}'. Expected 'lesson', 'assessment', or 'homework'.")
