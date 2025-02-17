from django.db import models

from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

class Subject(models.Model):
    
    MAX_SUBJECTS_PER_USER = 200

    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False) # must not be changed since creation
    name = models.CharField(max_length=150)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        if self.user.subject_set.count() >= self.MAX_SUBJECTS_PER_USER:
            raise ValidationError(
                message=f'You can\'t have more that {Subject.MAX_SUBJECTS_PER_USER} subjects per user.', 
                code='max_subjects_reached'
            )
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name