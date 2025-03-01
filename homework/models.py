from datetime import timedelta

from django.db import models
from django.utils.timezone import localtime, now
from django.core.exceptions import ValidationError

from subject.models import Subject
from lesson.models import Lesson

class HomeworkManager(models.Manager):

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        return obj

    def bulk_create(self, objs, **kwargs):
        for obj in objs:
            obj.full_clean()
        return super().bulk_create(objs, **kwargs)


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
                            'To fix this, either '
                            'select a lesson from the same subject as the homework, or '
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
                            'To fix this, either '
                            'select a lesson from the same subject as the homework, or '
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
                        solution = 'To fix this, choose two lessons from the same subject.'
                    ),  
                    code='subject_mismatch'
                )    
        
        return errors
   

    def validate_time_constraints(self):

        errors = {}

        ERROR_MESSAGE = '{entity} can\'t be set more than {days} days in the {direction}.'

        max_days = Homework.MAX_TIMEFRAME.days

        past_limit = now() - Homework.MAX_TIMEFRAME
        future_limit = now() + Homework.MAX_TIMEFRAME
        

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
            
        past_due_limit = now() - timedelta(days=30)

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
                code="past_due_date"
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

        super().save(*args, **kwargs)