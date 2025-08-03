from django.db import models
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from django.core.exceptions import ValidationError

from subject.models import Subject
from lesson.models import Lesson

from utils.accessors import get_subject, get_userprofile, get_time_display_format
from utils.constants import MAX_TASK_LENGTH, MAX_TIMEFRAME, RECENT_PAST_TIMEFRAME
from utils.reminder_time import should_schedule_reminder, calculate_scheduled_reminder_time
from utils.time_format import format_time

REMINDER_TRIGGER_FIELD = 'derived_due_at_prop'

class HomeworkManager(models.Manager):

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        return obj

    def bulk_create(self, objs, **kwargs):
        for obj in objs:
            obj.full_clean()
        return super().bulk_create(objs, **kwargs)
    
    def with_derived_fields(self):
        return self.annotate( # TO-DO: make sure homework is deleted when its subject is deleted, no matter if they are connected directly or via lesson
            derived_user_id = Coalesce('subject__user', 'lesson_given__subject__user', 'lesson_due__subject__user'),
            derived_subject_id=Coalesce('subject', 'lesson_given__subject', 'lesson_due__subject'),
            derived_start_time=Coalesce('start_time', 'lesson_given__start_time'),
            derived_due_at=Coalesce('due_at', 'lesson_due__start_time'),
        )


class Homework(models.Model):

    class Meta:
        db_table = 'homework'

        
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=True, null=True)
    lesson_given = models.ForeignKey(Lesson, on_delete=models.SET_NULL, blank=True, null=True, related_name='given_homework')
    lesson_due = models.ForeignKey(Lesson, on_delete=models.SET_NULL, blank=True, null=True, related_name='due_homework')
    start_time = models.DateTimeField(blank=True, null=True)
    due_at = models.DateTimeField(blank=True, null=True)
    task = models.CharField(max_length=MAX_TASK_LENGTH)
    completion_percent = models.IntegerField(default=0)
    has_subtasks = models.BooleanField(default=False)
    scheduled_reminder_time = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = HomeworkManager()

    @property
    def derived_subject(self):
        if hasattr(self, 'derived_subject_id'):
            return Subject.objects.get(id=self.derived_subject_id)
        return self.subject or (self.lesson_given and self.lesson_given.subject) or (self.lesson_due and self.lesson_due.subject)
    
    @property
    def derived_due_at_prop(self):
        return self.due_at or (self.lesson_due.start_time if self.lesson_due else None)
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_reminder_trigger_time = getattr(self, REMINDER_TRIGGER_FIELD)


    def clean(self):
        super().clean()

        errors = {}

        errors.update(self.validate_percentage())
        errors.update(self.validate_existence())
        errors.update(self.validate_subject_consistency())
        errors.update(self.validate_time_constraints())

        if errors:
            raise ValidationError(errors)

    
    def validate_percentage(self):

        errors = {}

        if not (0 <= self.completion_percent <= 100):
            errors['completion_percent'] = ValidationError(
                message='Completion percent must be between 0 and 100.',
                code='invalid_completion_percent'
            )

        return errors
        

    def validate_existence(self):

        errors = {}

        ERROR_MESSAGE = ('Homework must either have a {first_option} '
                        'or {second_option}.')
        
        if not self.subject and not self.lesson_given and not self.lesson_due:
            errors['__all__'] = ValidationError(
                message=ERROR_MESSAGE.format(
                    first_option='subject',
                    second_option='be linked to a lesson'
                ),
                code='required'
            )
        
        if not self.due_at and not self.lesson_due:
            errors['due_at'] = ValidationError(
                message=ERROR_MESSAGE.format(
                    first_option='due at date',
                    second_option='be due at a specific lesson'
                ),
                code='required'
            )
        
        return errors
    

    def validate_subject_consistency(self):

        errors = {}

        ERROR_MESSAGE = ('The selected {first_entity} belongs to "{first_subject}" '
                         'but {second_entity} is for "{second_subject}". '
                         'To fix this, {solution}.')

        if self.subject:
            if self.lesson_given and self.subject != self.lesson_given.subject:
                errors['lesson_given'] = ValidationError(
                    message=ERROR_MESSAGE.format(
                        first_entity='lesson the homework was given at',
                        first_subject=self.lesson_given.subject,
                        second_entity='this homework',
                        second_subject=self.subject,
                        solution = (
                            'either select a lesson from the same subject as the homework, or '
                            'remove either the lesson or the subject so the remaining one is used.'
                        )
                    ),  
                    code='subject_mismatch'
                )
            
            if self.lesson_due and self.subject != self.lesson_due.subject:
                errors['lesson_due'] = ValidationError(
                    message=ERROR_MESSAGE.format(
                        first_entity='lesson the homework is due at',
                        first_subject=self.lesson_due.subject,
                        second_entity='this homework',
                        second_subject=self.subject,
                        solution = (
                            'either select a lesson from the same subject as the homework, or '
                            'remove either the lesson or the subject so the remaining one is used.'
                        )
                    ),  
                    code='subject_mismatch'
                )
            
        if self.lesson_given and self.lesson_due and self.lesson_given.subject != self.lesson_due.subject:
            errors['__all__'] = ValidationError(
                    message=ERROR_MESSAGE.format(
                        first_entity='lesson the homework was given at',
                        first_subject=self.lesson_given.subject,
                        second_entity='lesson the homework is due at',
                        second_subject=self.lesson_due.subject,
                        solution = 'choose two lessons from the same subject.'
                    ),  
                    code='subject_mismatch'
                )    
        
        return errors
   

    def validate_time_constraints(self):

        errors = {}

        ERROR_MESSAGE = '{entity} can\'t be set more than {days} days in the {direction}.'

        max_days = MAX_TIMEFRAME.days

        past_limit = now() - MAX_TIMEFRAME
        future_limit = now() + MAX_TIMEFRAME
        

        for field_value, field_name, label in [
            (self.start_time, 'start_time', 'Homework start time'),
            (self.lesson_given.start_time if self.lesson_given else None, 'lesson_given', 'Lesson homework was given at'),
        ]:
            if field_value and field_value < past_limit:
                errors[field_name] = ValidationError(
                    message=ERROR_MESSAGE.format(
                        entity=label,
                        days=max_days,
                        direction='past',
                    ),
                    code='past_limit_exceeded'
                )

        for field_value, field_name, label in [
            (self.start_time, 'start_time', 'Homework start time'),
            (self.due_at, 'due_at', 'Homework due time'),
            (self.lesson_due.start_time if self.lesson_due else None, 'lesson_due', 'Lesson homework is due to'),
        ]:
            if field_value and field_value > future_limit:
                errors[field_name] = ValidationError(
                    message=ERROR_MESSAGE.format(
                        entity=label,
                        days=max_days,
                        direction='future',
                    ),
                    code='future_limit_exceeded'
                )
            
        past_due_limit = now() - RECENT_PAST_TIMEFRAME

        for field_value, field_name, label in [
            (self.due_at, 'due_at', 'Homework due date'),
            (self.lesson_due.start_time if self.lesson_due else None, 'lesson_due', 'Lesson homework is due at')
        ]:
            if field_value and field_value < past_due_limit:
                errors[field_name] = ValidationError(
                message=ERROR_MESSAGE.format(
                    entity=label,
                    days=30,
                    direction='past',
                ),
                code='past_due_date'
            )
                
        if self.lesson_given and self.lesson_given.start_time > now():
            errors['lesson_given'] = ValidationError(
                message='Homework can\'t be assigned to lesson starting in the future',
                code='invalid_given_time'
            )
        

        fields = [
            (self.due_at, 'due_at', 'homework due date'),
            (self.lesson_due.start_time if self.lesson_due else None, 'lesson_due', 'lesson homework is due at')
        ]

        if self.start_time:

            ERROR_MESSAGE = 'Homework start time must be earlier than {entity}.'

            for field_value, field_name, label in fields:
                if field_value and field_value <= self.start_time:
                    errors[field_name] = ValidationError(
                        message=ERROR_MESSAGE.format(
                            entity=label
                        ),
                        code='invalid_start_order'
                    )


        if self.lesson_given:

            ERROR_MESSAGE = 'Lesson homework was given at start time must be earlier than {entity}.'

            for field_value, field_name, label in fields:
                if field_value and field_value <= self.lesson_given.start_time:
                    errors[field_name] = ValidationError(
                        message=ERROR_MESSAGE.format(
                            entity=label
                        ),
                        code='invalid_start_order'
                    )
                

        return errors


    def save(self, *args, **kwargs):
        self.full_clean()

        if self.lesson_given or self.lesson_due:
            self.subject = None

        if not self.start_time and not self.lesson_given:
            self.start_time = now()

        if self.start_time and self.lesson_given and self.start_time == self.lesson_given.start_time:
            self.start_time = None
            
        if self.due_at and self.lesson_due and self.due_at == self.lesson_due.start_time:
            self.due_at = None

        userprofile = get_userprofile(self)
        if should_schedule_reminder(self, userprofile, 'homework', REMINDER_TRIGGER_FIELD):
            self.scheduled_reminder_time = calculate_scheduled_reminder_time(
                instance=self,
                userprofile=userprofile,
                event_type='homework'
            )

        super().save(*args, **kwargs)
        self._original_reminder_trigger_time = getattr(self, REMINDER_TRIGGER_FIELD)


    def __str__(self):
        subject = get_subject(self)

        if hasattr(self, 'derived_due_at'):
            date = self.derived_due_at
        else:
            date = self.derived_due_at_prop
 
        return f'{subject} homework: {self.task[0].lower()}{self.task[1:50]}... (Due: {format_time(date, get_time_display_format(self))}'