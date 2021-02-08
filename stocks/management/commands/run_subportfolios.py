from django.core.management.base import BaseCommand
from stocks.tasks import run_subportfolios, check_positions_on_brokerage, run_positions_on_brokerage
from stocks.eastern_time import EST5EDT
import datetime
from stocks.rh_utils import is_market_open, trading_login
import logging


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = datetime.datetime.now(tz=EST5EDT())
        weekday = now.weekday()
        if weekday < 5:
            trading_login()
            if is_market_open():
                run_subportfolios.apply_async(countdown=0)
                run_subportfolios.apply_async(countdown=5*60)

                run_positions_on_brokerage.apply_async(countdown=0)
                check_positions_on_brokerage.apply_async(countdown=1*60)
                run_positions_on_brokerage.apply_async(countdown=2*60)
                check_positions_on_brokerage.apply_async(countdown=3*60)
                run_positions_on_brokerage.apply_async(countdown=4*60)
                check_positions_on_brokerage.apply_async(countdown=5*60)
                run_positions_on_brokerage.apply_async(countdown=6*60)
                check_positions_on_brokerage.apply_async(countdown=7*60)


