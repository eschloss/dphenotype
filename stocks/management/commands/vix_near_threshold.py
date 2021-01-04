from django.core.management.base import BaseCommand
from stocks.tasks import vix_near_threshold
from stocks.eastern_time import EST5EDT
import datetime
import logging


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = datetime.datetime.now(tz=EST5EDT())
        hour = now.hour
        weekday = now.weekday()
        if weekday < 5 and 4 < hour < 20:
            vix_near_threshold.apply_async(countdown=0)
            vix_near_threshold.apply_async(countdown=5*60)
