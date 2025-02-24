# Generated by Django 5.1.6 on 2025-02-24 15:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0004_alter_assessment_table'),
        ('lesson', '0004_alter_lesson_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='lesson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lesson.lesson'),
        ),
    ]
