from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from utils.constants import MAX_SUBJECTS_PER_USER, MAX_SUBJECT_NAME_LENGTH

class SubjectManager(models.Manager):

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        return obj
    
    def bulk_create(self, objs, **kwargs):
        for obj in objs:
            obj.full_clean()
        return super().bulk_create(objs, **kwargs)
    

class Subject(models.Model):

    class Meta:
        db_table = 'subject'

    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False) # must not be changed since creation
    name = models.CharField(max_length=MAX_SUBJECT_NAME_LENGTH)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = SubjectManager()

    def clean(self):
        super().clean()

        errors = {}

        if self.user.subject_set.count() >= MAX_SUBJECTS_PER_USER:
            errors['user'] = ValidationError(
                message=f'You can\'t have more that {MAX_SUBJECTS_PER_USER} subjects per user.', 
                code='max_subjects_reached'
            )
        
        if errors:
            raise ValidationError(errors)
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name