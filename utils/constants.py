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
MIN_ASSESSMENT_DURATION = timedelta(minutes=15)
MAX_ASSESSMENT_DURATION = timedelta(hours=8)

# ---- Homework ----
MAX_TIMEFRAME = timedelta(days=365)
RECENT_PAST_TIMEFRAME = timedelta(days=30)
MAX_TASK_LENGTH = 1000