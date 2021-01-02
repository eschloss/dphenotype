from django.core.management.base import BaseCommand
from stocks.tasks import send_vix_data


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        send_vix_data.delay()
