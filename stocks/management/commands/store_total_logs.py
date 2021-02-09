from django.core.management.base import BaseCommand
from stocks.tasks import store_total_logs


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        store_total_logs.apply_async(countdown=0)

