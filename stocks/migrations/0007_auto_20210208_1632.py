# Generated by Django 3.1.4 on 2021-02-08 16:32

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0006_auto_20210208_1244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subportfolio',
            name='run_hour',
            field=models.FloatField(default=0.95),
        ),
        migrations.CreateModel(
            name='CashAtDayStart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.DecimalField(decimal_places=8, default=0, max_digits=16)),
                ('agg_last_run', models.DateTimeField(default=datetime.datetime(2014, 9, 12, 11, 19, 54))),
                ('userportfolio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stocks.userportfolio')),
            ],
        ),
    ]