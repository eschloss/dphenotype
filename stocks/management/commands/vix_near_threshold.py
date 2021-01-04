from django.core.management.base import BaseCommand
from stocks.tasks import vix_near_threshold
import logging


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        vix_near_threshold.delay()
