from django.core.management.base import BaseCommand
from stocks.tasks import run_subportfolios
from stocks.eastern_time import EST5EDT
import datetime
from rh_utils import is_market_open, trading_login
import logging


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = datetime.datetime.now(tz=EST5EDT())
        weekday = now.weekday()
        if weekday < 5:
            trading_login()
            if is_market_open():
                run_subportfolio.apply_async(countdown=0)
                run_subportfolio.apply_async(countdown=5*60)

