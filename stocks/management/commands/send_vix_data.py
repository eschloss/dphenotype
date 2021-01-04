from django.core.management.base import BaseCommand
from stocks.tasks import send_vix_data
from stocks.eastern_time import EST5EDT
import datetime
import logging


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = datetime.datetime.now(tz=EST5EDT())
        weekday = now.weekday()
        if weekday < 5:
            send_vix_data.delay()

