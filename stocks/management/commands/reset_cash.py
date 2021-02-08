from django.core.management.base import BaseCommand
from stocks.tasks import reset_userportfolio_cash
from stocks.eastern_time import EST5EDT
import datetime


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        reset_userportfolio_cash.apply_async(countdown=0)

