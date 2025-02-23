from datetime import timedelta

from django.db import models
from django.utils.timezone import localtime, now
from django.core.exceptions import ValidationError

from subject.models import Subject
from lesson.models import Lesson

class Homework(models.Model):

    class Meta:
        db_table = 'homework'

    MAX_TIMEFRAME = timedelta(days=365)

        
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=True, null=True)
    lesson_given = models.ForeignKey(Lesson, on_delete=models.SET_NULL, blank=True, null=True, related_name="given_homeworks")
    lesson_due = models.ForeignKey(Lesson, on_delete=models.SET_NULL, blank=True, null=True, related_name="due_homeworks")
    start_time = models.DateTimeField(blank=True, null=True)
    due_at = models.DateTimeField(blank=True, null=True)
    task = models.CharField(max_length=1000)
    completion_percent = models.IntegerField(default=0)
    has_subtasks = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        self.validate_percentage()
        self.validate_existence()
        self.validate_subject_consistency()
        self.validate_time_constraints()

    
    def validate_percentage(self):
        if not (0 <= self.completion_percent <= 100):
            raise ValidationError(
                message='Completion percent must be between 0 and 100.',
                code='invalid_completion_percent'
            )
        
    
    def validate_subject_consistency(self):

        ERROR_MESSAGE = ('The selected {first_entity} belongs to "{first_subject}" '
                         'but {second_entity} is for "{second subject}". '
                         'To fix this, {solution}.')

        if self.subject:
            if self.lesson_given and self.subject != self.lesson_given.subject:
                raise ValidationError(
                    message=ERROR_MESSAGE.format(
                        first_entity='lesson the homework was given at',
                        first_subject=self.lesson_given.subject,
                        second_entity='this homework',
                        second_subject=self.subject,
                        solution = (
                            'To fix this, either '
                            'select a lesson from the same subject as the homework, or '
                            'remove either the lesson or the subject so the remaining one is used.'
                        )
                    ),  
                    code='subject_mismatch'
                )
            
            if self.lesson_due and self.subject != self.lesson_due.subject:
                raise ValidationError(
                    message=ERROR_MESSAGE.format(
                        first_entity='lesson the homework is due at',
                        first_subject=self.lesson_due.subject,
                        second_entity='this homework',
                        second_subject=self.subject,
                        solution = (
                            'To fix this, either '
                            'select a lesson from the same subject as the homework, or '
                            'remove either the lesson or the subject so the remaining one is used.'
                        )
                    ),  
                    code='subject_mismatch'
                )
            
        if self.lesson_given and self.lesson_due and self.lesson_given.subject != self.lesson_due.subject:
            raise ValidationError(
                    message=ERROR_MESSAGE.format(
                        first_entity='lesson the homework was given at',
                        first_subject=self.lesson_given.subject,
                        second_entity='lesson the homework is due at',
                        second_subject=self.lesson_due.subject,
                        solution = 'To fix this, choose two lessons from the same subject.'
                    ),  
                    code='subject_mismatch'
                )    


    def validate_existence(self):

        ERROR_MESSAGE = ('Homework must either have a {first_option} '
                         'or {second_option}.'
                        )
        
        if not self.subject and not self.lesson_given and not self.lesson_due:
            raise ValidationError(
                message=ERROR_MESSAGE.format(
                    first_option='subject',
                    second_option='be linked to a lesson'
                ),
                code='required'
            )
        
        if not self.due_at and not self.lesson_due:
            raise ValidationError(
                message=ERROR_MESSAGE.format(
                    first_option='due at date',
                    second_option='be due at a specific lesson'
                ),
                code='required'
            )
   

    def validate_time_constraints(self):

        ERROR_MESSAGE = '{entity} can\'t be set more than {days} days in the {direction}.'

        max_days = Homework.MAX_TIMEFRAME.days

        past_limit = now() - Homework.MAX_TIMEFRAME
        future_limit = now() + Homework.MAX_TIMEFRAME
        
        for field, label in [
            (self.start_time, 'Homework start time'),
            (self.lesson_given.start_time if self.lesson_given else None, 'Lesson homework was given at'),
        ]:
            if field and field < past_limit:
                raise ValidationError(
                    message=ERROR_MESSAGE.format(
                        entity=label,
                        days=max_days,
                        direction='past',
                    ),
                    code='past_limit_exceeded'
                )

        for field, label in [
            (self.start_time, 'Homework start time'),
            (self.due_at, 'Homework due time'),
            (self.lesson_due.start_time if self.lesson_due else None, 'Lesson homework is due to'),
        ]:
            if field and field > future_limit:
                raise ValidationError(
                    message=ERROR_MESSAGE.format(
                        entity=label,
                        days=max_days,
                        direction='future',
                    ),
                    code='future_limit_exceeded'
                )
                
        if self.lesson_given and self.lesson_given.start_time > now():
            raise ValidationError(
                message='Homework can\'t be assigned to lesson starting in the future',
                code='invalid_given_time'
            )
        
        past_due_limit = now() - timedelta(days=30)

        if self.due_at and self.due_at < past_due_limit:
            raise ValidationError(
                message="Homework due date can't be more than 30 days in the past.",
                code="past_due_date"
            )

        fields = [
            (self.due_at, 'homework due date'),
            (self.lesson_due.start_time if self.lesson_due else None, 'lesson homework is due at')
        ]

        if self.start_time:

            ERROR_MESSAGE = 'Homework start time must be earlier then {entity}.'

            for field, label in fields:
                if field and field <= self.start_time:
                    raise ValidationError(
                        message=ERROR_MESSAGE.format(
                            entity=label
                        ),
                        code='invalid_start_order'
                    )


        if self.lesson_given:

            ERROR_MESSAGE = 'Lesson homework was given at start time must be earlier then {entity}.'

            for field, label in fields:
                if field and field <= self.lesson_given.start_time:
                    raise ValidationError(
                        message=ERROR_MESSAGE.format(
                            entity=label
                        ),
                        code='invalid_start_order'
                    )


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

        super().save(*args, **kwargs)