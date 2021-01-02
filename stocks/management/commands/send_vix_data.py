from django.core.management.base import BaseCommand
from stocks.tasks import send_vix_data
import logging


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        send_vix_data() #can't get celery to work properly
        logging.info("send_vix_data request made - celery")
        print("send_vix_data request made - celery")
