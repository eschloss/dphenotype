# Generated by Django 3.1.4 on 2021-04-21 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20210421_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionsection',
            name='dependent_question_answers',
            field=models.CharField(blank=True, help_text='Choose the answer(s) necessary for the dependent quesiton in order to show this question. Separate multiple acceptable answers with a comma.', max_length=100, null=True),
        ),
    ]
