# Generated by Django 3.1.4 on 2023-06-06 12:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_validstudyid_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_am_push',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='last_pm_push',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='next_random',
            field=models.FloatField(default=16),
        ),
        migrations.AlterField(
            model_name='freetextquestiontemplate',
            name='is_dependent_on_question',
            field=models.BooleanField(default=False, help_text='Is this question dependent on the answer to other questions?'),
        ),
        migrations.AlterField(
            model_name='multiplechoicequestiontemplate',
            name='is_dependent_on_question',
            field=models.BooleanField(default=False, help_text='Is this question dependent on the answer to other questions?'),
        ),
        migrations.AlterField(
            model_name='numberquestiontemplate',
            name='is_dependent_on_question',
            field=models.BooleanField(default=False, help_text='Is this question dependent on the answer to other questions?'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='pm',
            field=models.FloatField(default=20, help_text='Military time in US Eastern time - must be earlier than 24 (before midnight)'),
        ),
    ]
