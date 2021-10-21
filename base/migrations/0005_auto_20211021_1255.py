# Generated by Django 3.1.4 on 2021-10-21 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20210425_1515'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='freetextquestiontemplate',
            name='frequency_interval',
        ),
        migrations.RemoveField(
            model_name='multiplechoicequestiontemplate',
            name='frequency_interval',
        ),
        migrations.RemoveField(
            model_name='numberquestiontemplate',
            name='frequency_interval',
        ),
        migrations.AddField(
            model_name='freetextquestioninstance',
            name='last_notification',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='freetextquestioninstance',
            name='notification_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='freetextquestiontemplate',
            name='dependent_question',
            field=models.ForeignKey(blank=True, help_text='Choose the dependent question', null=True, on_delete=django.db.models.deletion.CASCADE, to='base.multiplechoicequestiontemplate'),
        ),
        migrations.AddField(
            model_name='freetextquestiontemplate',
            name='dependent_question_answers',
            field=models.CharField(blank=True, help_text='Choose the answer(s) necessary for the dependent quesiton in order to show this question. Separate multiple acceptable answers with a comma.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='freetextquestiontemplate',
            name='frequency_days',
            field=models.IntegerField(blank=True, default=1, help_text='Days until the next time the question is asked. (only fill-in for routine questions).', null=True),
        ),
        migrations.AddField(
            model_name='freetextquestiontemplate',
            name='frequency_time',
            field=models.CharField(choices=[('a', 'AM'), ('p', 'PM')], default=1, max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='freetextquestiontemplate',
            name='is_dependent_on_questions',
            field=models.BooleanField(default=False, help_text='Is this section dependent on the answer to other questions?'),
        ),
        migrations.AddField(
            model_name='freetextquestiontemplate',
            name='send_notification',
            field=models.BooleanField(default=False, help_text='does a notification go out for this particular question?'),
        ),
        migrations.AddField(
            model_name='freetextquestiontemplate',
            name='threshold',
            field=models.TextField(blank=True, default='', help_text='comma separated list of threshold triggering words', null=True),
        ),
        migrations.AddField(
            model_name='freetextquestiontemplate',
            name='who_receives',
            field=models.CharField(choices=[('y', 'youth'), ('b', 'both youth and caretaker')], default='y', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='multiplechoicequestioninstance',
            name='last_notification',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='multiplechoicequestioninstance',
            name='notification_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='multiplechoicequestiontemplate',
            name='dependent_question',
            field=models.ForeignKey(blank=True, help_text='Choose the dependent question', null=True, on_delete=django.db.models.deletion.CASCADE, to='base.multiplechoicequestiontemplate'),
        ),
        migrations.AddField(
            model_name='multiplechoicequestiontemplate',
            name='dependent_question_answers',
            field=models.CharField(blank=True, help_text='Choose the answer(s) necessary for the dependent quesiton in order to show this question. Separate multiple acceptable answers with a comma.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='multiplechoicequestiontemplate',
            name='frequency_days',
            field=models.IntegerField(blank=True, default=1, help_text='Days until the next time the question is asked. (only fill-in for routine questions).', null=True),
        ),
        migrations.AddField(
            model_name='multiplechoicequestiontemplate',
            name='frequency_time',
            field=models.CharField(choices=[('a', 'AM'), ('p', 'PM')], default=1, max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='multiplechoicequestiontemplate',
            name='is_dependent_on_questions',
            field=models.BooleanField(default=False, help_text='Is this section dependent on the answer to other questions?'),
        ),
        migrations.AddField(
            model_name='multiplechoicequestiontemplate',
            name='send_notification',
            field=models.BooleanField(default=False, help_text='does a notification go out for this particular question?'),
        ),
        migrations.AddField(
            model_name='multiplechoicequestiontemplate',
            name='threshold',
            field=models.TextField(blank=True, default='', help_text='comma separated list of threshold triggering words', null=True),
        ),
        migrations.AddField(
            model_name='multiplechoicequestiontemplate',
            name='who_receives',
            field=models.CharField(choices=[('y', 'youth'), ('b', 'both youth and caretaker')], default='y', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='numberquestioninstance',
            name='last_notification',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='numberquestioninstance',
            name='notification_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='numberquestiontemplate',
            name='dependent_question',
            field=models.ForeignKey(blank=True, help_text='Choose the dependent question', null=True, on_delete=django.db.models.deletion.CASCADE, to='base.multiplechoicequestiontemplate'),
        ),
        migrations.AddField(
            model_name='numberquestiontemplate',
            name='dependent_question_answers',
            field=models.CharField(blank=True, help_text='Choose the answer(s) necessary for the dependent quesiton in order to show this question. Separate multiple acceptable answers with a comma.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='numberquestiontemplate',
            name='frequency_days',
            field=models.IntegerField(blank=True, default=1, help_text='Days until the next time the question is asked. (only fill-in for routine questions).', null=True),
        ),
        migrations.AddField(
            model_name='numberquestiontemplate',
            name='frequency_time',
            field=models.CharField(choices=[('a', 'AM'), ('p', 'PM')], default=1, max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='numberquestiontemplate',
            name='is_dependent_on_questions',
            field=models.BooleanField(default=False, help_text='Is this section dependent on the answer to other questions?'),
        ),
        migrations.AddField(
            model_name='numberquestiontemplate',
            name='send_notification',
            field=models.BooleanField(default=False, help_text='does a notification go out for this particular question?'),
        ),
        migrations.AddField(
            model_name='numberquestiontemplate',
            name='threshold',
            field=models.TextField(blank=True, default='', help_text='comma separated list of threshold triggering words', null=True),
        ),
        migrations.AddField(
            model_name='numberquestiontemplate',
            name='who_receives',
            field=models.CharField(choices=[('y', 'youth'), ('b', 'both youth and caretaker')], default='y', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='am',
            field=models.FloatField(default=8, help_text='Military time in US Eastern time'),
        ),
        migrations.AddField(
            model_name='profile',
            name='pm',
            field=models.FloatField(default=20, help_text='Military time in US Eastern time'),
        ),
        migrations.AddField(
            model_name='profile',
            name='type',
            field=models.CharField(choices=[('y', 'youth'), ('c', 'caretaker')], default='y', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='questiongroup',
            name='send_notification',
            field=models.BooleanField(default=False, help_text='does a notification go out for this particular group?'),
        ),
        migrations.AddField(
            model_name='questionsection',
            name='is_static',
            field=models.BooleanField(default=False, help_text='Is this section part of the static section?'),
        ),
        migrations.AlterField(
            model_name='freetextquestiontemplate',
            name='one_time_only',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='multiplechoicequestiontemplate',
            name='one_time_only',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='numberquestiontemplate',
            name='one_time_only',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='questionsection',
            name='is_baseline',
            field=models.BooleanField(default=False, help_text='Is this section part of a baseline questionnaire?'),
        ),
    ]
