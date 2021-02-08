from django.core.management.base import BaseCommand
from stocks.tasks import run_subportfolios
from stocks.eastern_time import EST5EDT
import datetime
import logging


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = datetime.datetime.now(tz=EST5EDT())
        weekday = now.weekday()
        if weekday < 5:
            run_subportfolios.delay()

