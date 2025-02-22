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

        self.validate_existence()
        self.validate_subject_consistency()
        self.validate_time_constraints()
        
    
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
                    second_option='be due specific lesson'
                ),
                code='required'
            )
   


    def validate_time_constraints(self):

        ERROR_MESSAGE = '{entity} can\'nt {} more than {days} days {direction}.'

        max_days = Homework.MAX_TIMEFRAME.days

        past_limit = now() - Homework.MAX_TIMEFRAME
        future_limit = now() + Homework.MAX_TIMEFRAME
        
        if self.start_time and self.start_time < now() - Homework.MAX_TIMEFRAME:
            raise ValidationError(
                message='Homework can\'nt start more that {Homework.MAX_TIMEFRAME} in the past.',
                code=''
            )
        
        if self.lesson_given and self.lesson_given.start_time < now() - Homework.MAX_TIMEFRAME:
            raise ValidationError(
                message='Lesson homework was given at can\'nt start more that {Homework.MAX_TIMEFRAME} in the past.',
                code=''
            )
       
        if self.due_at and self.start_time > now() + Homework.MAX_TIMEFRAME:
            raise ValidationError(
                message='Homework can\'nt be due more that {Homework.MAX_TIMEFRAME} in the future.',
                code=''
            )
        
        if self.lesson_due and self.lesson_due.start_time > now() + Homework.MAX_TIMEFRAME:
            raise ValidationError(
                message='Lesson homework is due at can\'nt start more that {Homework.MAX_TIMEFRAME} in the future.',
                code=''
            )
        
        if self.start_time:
            if self.due_at and self.start_time >= self.due_at:
                raise ValidationError(
                    message='Start time must be smaller then due_at',
                    code=''
                )

            if self.lesson_due and self.start_time >= self.lesson_due.start_time:
                raise ValidationError(
                    message='Start time must be smaller then lesson due start time',
                    code=''
                )

        if self.lesson_given:
            if self.due_at and self.lesson_given.start_time >= self.due_at:
                raise ValidationError(
                    message='Lesson given start_time time must be smaller then due_at',
                    code=''
                )
            
            if self.lesson_due and self.lesson_given.start_time >= self.lesson_due.start_time:
                raise ValidationError(
                    message='Lesson given start_time time must be smaller then lesson_due start_time',
                    code=''
                )


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save()