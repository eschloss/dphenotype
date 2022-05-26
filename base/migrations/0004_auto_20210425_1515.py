# Generated by Django 3.1.4 on 2021-04-25 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20210421_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='freetextquestioninstance',
            name='question_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.freetextquestiontemplate'),
        ),
        migrations.AlterField(
            model_name='freetextquestiontemplate',
            name='question_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.questiongroup'),
        ),
        migrations.AlterField(
            model_name='multiplechoicequestioninstance',
            name='question_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.multiplechoicequestiontemplate'),
        ),
        migrations.AlterField(
            model_name='multiplechoicequestiontemplate',
            name='question_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.questiongroup'),
        ),
        migrations.AlterField(
            model_name='numberquestioninstance',
            name='question_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.numberquestiontemplate'),
        ),
        migrations.AlterField(
            model_name='numberquestiontemplate',
            name='question_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.questiongroup'),
        ),
        migrations.AlterField(
            model_name='questiongroup',
            name='question_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.questionsection'),
        ),
        migrations.AlterField(
            model_name='questionsection',
            name='dependent_question',
            field=models.ForeignKey(blank=True, help_text='Choose the dependent question', null=True, on_delete=django.db.models.deletion.CASCADE, to='base.multiplechoicequestiontemplate'),
        ),
    ]