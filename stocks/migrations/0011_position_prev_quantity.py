# Generated by Django 3.1.4 on 2021-02-11 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0010_auto_20210209_2335'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='prev_quantity',
            field=models.DecimalField(decimal_places=8, default=0, max_digits=16),
        ),
    ]