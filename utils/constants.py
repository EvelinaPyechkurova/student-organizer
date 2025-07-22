from datetime import timedelta

# -- -- General ----
VALID_TIMEFRAME_OPTIONS = [
    ('today', 'Today'),
    ('tomorrow', 'Tomorrow'),
    ('next3', 'Next 3 Days'),
    ('this_week', 'This Week'),
    ('next_week', 'Next Week'),
    ('this_month', 'This Month'),
    ('next_month', 'Next Month'),
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

DEFAULT_RECIEVE_LESSON_REMINDERS = False
DEFAULT_LESSON_REMINDER_TIMING = timedelta(hours=1)

DEFAULT_RECIEVE_ASSESSMENT_REMINDERS = True
DEFAULT_ASSESSMENT_REMINDER_TIMING = timedelta(days=3)

DEFAULT_RECIEVE_HOMEWORK_REMINDERS = True
DEFAULT_HOMEWORK_REMINDER_TIMING = timedelta(days=2)