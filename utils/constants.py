from datetime import timedelta

# ---- Filtering and Sorting ----
VALID_TIMEFRAME_OPTIONS = [
    ('day', 'Today'),
    ('next_day', 'Tomorrow'),
    ('next_3_days', 'Next 3 Days'),
    ('week', 'This Week'),
    ('next_week', 'Next Week'),
    ('month', 'This Month'),
    ('next_month', 'Next Month'),
]

DEFAULT_SORTING_OPTIONS = [
    ('created_at', 'Created At ⭡'),
    ('-created_at', 'Created At ⭣'),
]

# ----- Subject ----
MAX_SUBJECTS_PER_USER = 200
MAX_SUBJECT_NAME_LENGTH = 150

# ----- Lesson -----
MIN_LESSON_DURATION = timedelta(minutes=15)
MAX_LESSON_DURATION = timedelta(hours=8)

# --- Assessment ---
MIN_ASSESSMENT_DURATION = timedelta(minutes=5)
MAX_ASSESSMENT_DURATION = timedelta(days=7)

# ---- Homework ----
MAX_TIMEFRAME = timedelta(days=365)
RECENT_PAST_TIMEFRAME = timedelta(days=30)
MAX_TASK_LENGTH = 1000

# -- User Profile --
DEFAULT_LESSON_DURATION = timedelta(minutes=90)

DEFAULT_RECEIVE_LESSON_REMINDERS = False
DEFAULT_LESSON_REMINDER_TIMING = timedelta(hours=1)

DEFAULT_RECEIVE_ASSESSMENT_REMINDERS = True
DEFAULT_ASSESSMENT_REMINDER_TIMING = timedelta(days=3)

DEFAULT_RECEIVE_HOMEWORK_REMINDERS = True
DEFAULT_HOMEWORK_REMINDER_TIMING = timedelta(days=2)

# -- Event Type Specific Messages --
EVENT_TYPE_SPECIFIC_EMAIL_MESSAGES = {
    'lesson': 'Make sure to attend on time and be prepared.',
    'assessment': 'Make sure to revise the material and prepare well.',
    'homework': "Don't forget to finish and submit your assignment.",
}
