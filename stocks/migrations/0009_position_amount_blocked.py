# Generated by Django 3.1.4 on 2021-02-09 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0008_position_settled_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='amount_blocked',
            field=models.DecimalField(decimal_places=8, default=0, max_digits=16),
        ),
    ]