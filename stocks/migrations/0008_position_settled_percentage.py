# Generated by Django 3.1.4 on 2021-02-09 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0007_auto_20210208_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='settled_percentage',
            field=models.DecimalField(decimal_places=8, default=0, max_digits=9),
        ),
    ]
