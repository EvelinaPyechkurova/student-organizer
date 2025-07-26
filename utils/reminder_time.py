USER_REMINDER_ENABLED_FIELD = 'receive_{event_type}_reminders'
USER_REMINDER_TIMING_FIELD = '{event_type}_reminder_timing'

def is_reminder_enabled(userprofile, event_type: str):
    '''
    Returns True if the user has enabled reminders for the given event type.
    '''
    return getattr(userprofile, USER_REMINDER_ENABLED_FIELD.format(event_type=event_type))


def should_schedule_reminder(instance, userprofile, event_type: str):
    '''
    Determines whether a reminder should be scheduled for the given instance.
    Checks that it has not already been scheduled, and that the user has enabled reminders.
    '''
    return (
        instance.scheduled_reminder_time is None
        and is_reminder_enabled(userprofile, event_type)
    )


def get_reminder_timing_from_user_profile(userprofile, event_type: str):
    '''
    Returns reminder timing for the given event type
    (lesson, assessment, homework) from the user's profile.
    '''
    try:
        return getattr(userprofile, USER_REMINDER_TIMING_FIELD.format(event_type=event_type))
    except AttributeError:
        raise AttributeError(f'UserProfile has no reminder timing for event type "{event_type}".')


def calculate_scheduled_reminder_time(instance, userprofile, event_type: str):
    '''
    Calculates the exact datetime when the reminder should be sent,
    based on user preferences and the event's start or due time.
    '''
    event_trigger_times = {
        'lesson': lambda instance: instance.start_time,
        'assessment': lambda instance: instance.derived_start_time_prop,
        'homework': lambda instance: instance.derived_due_at_prop,
    }

    reminder_timing = get_reminder_timing_from_user_profile(userprofile, event_type)

    try:
        return event_trigger_times[event_type](instance) - reminder_timing
    except KeyError:
        raise ValueError(f"Unknown event type: '{event_type}'. Expected 'lesson', 'assessment', or 'homework'.")
