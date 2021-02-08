# Generated by Django 3.1.4 on 2021-02-05 22:47

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SubPortfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategy', models.CharField(choices=[(0, 'Sector Strategy 1')], max_length=3)),
                ('points', models.IntegerField(default=1)),
                ('notes', models.TextField(blank=True, null=True)),
                ('run_hour', models.FloatField(default=15.9)),
                ('is_being_run_currently_lock', models.BooleanField(default=False)),
                ('agg_pc_of_total', models.FloatField(default=1)),
                ('agg_last_run', models.DateTimeField(default=datetime.datetime(2014, 9, 12, 11, 19, 54))),
                ('agg_total', models.DecimalField(decimal_places=8, max_digits=16)),
                ('agg_total_last_set', models.DateTimeField(default=datetime.datetime(2014, 9, 12, 11, 19, 54))),
            ],
        ),
        migrations.CreateModel(
            name='UserPortfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('on', models.BooleanField(default=True)),
                ('account_id', models.CharField(max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=15)),
                ('quantity', models.DecimalField(decimal_places=8, max_digits=16)),
                ('transaction_date', models.DateTimeField()),
                ('transaction_id', models.URLField()),
                ('subportfolio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stocks.subportfolio')),
            ],
        ),
        migrations.AddField(
            model_name='subportfolio',
            name='userportfolio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stocks.userportfolio'),
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=15)),
                ('current_quantity', models.DecimalField(decimal_places=8, max_digits=16)),
                ('goal_percentage', models.DecimalField(decimal_places=8, max_digits=9)),
                ('first_transaction_date', models.DateTimeField(auto_now_add=True)),
                ('last_edit_date', models.DateTimeField(auto_now=True)),
                ('sold', models.BooleanField(default=False)),
                ('placed_on_brokerage', models.BooleanField(default=False)),
                ('settled', models.BooleanField(default=False)),
                ('position_id', models.URLField()),
                ('instrument_id', models.URLField()),
                ('agg_total', models.DecimalField(decimal_places=8, max_digits=16)),
                ('agg_total_last_set', models.DateTimeField(default=datetime.datetime(2014, 9, 12, 11, 19, 54))),
                ('subportfolio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stocks.subportfolio')),
            ],
        ),
    ]