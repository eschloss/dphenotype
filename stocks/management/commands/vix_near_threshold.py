from django.core.management.base import BaseCommand
from stocks.tasks import vix_near_threshold
from stocks.eastern_time import EST5EDT
import datetime
from stocks.rh_utils import is_market_open, trading_login
import logging


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = datetime.datetime.now(tz=EST5EDT())
        hour = now.hour
        weekday = now.weekday()
        if weekday < 5:
            trading_login()
            if is_market_open():
                vix_near_threshold.apply_async(countdown=0)
                vix_near_threshold.apply_async(countdown=5*60)
