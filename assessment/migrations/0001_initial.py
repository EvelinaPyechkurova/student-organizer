# Generated by Django 5.1.6 on 2025-02-13 21:14

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lesson', '0002_alter_lesson_type'),
        ('subject', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('T', 'Test'), ('Q', 'Quiz'), ('E', 'Exam'), ('M', 'Midterm'), ('O', 'Oral Exam'), ('L', 'Lab Work'), ('S', 'Essay'), ('P', 'Project')], default='T', max_length=1)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('duration_minutes', models.DurationField(default=datetime.timedelta(seconds=5400))),
                ('description', models.CharField(max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lesson.lesson')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subject.subject')),
            ],
        ),
    ]
