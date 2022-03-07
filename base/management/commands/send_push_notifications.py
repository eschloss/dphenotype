from django.core.management.base import BaseCommand
from base.tasks import send_push_notifications


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        send_push_notifications.delay()


