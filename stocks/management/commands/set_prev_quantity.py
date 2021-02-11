from django.core.management.base import BaseCommand
from stocks.tasks import set_prev_quantity


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        set_prev_quantity.apply_async(countdown=0)


