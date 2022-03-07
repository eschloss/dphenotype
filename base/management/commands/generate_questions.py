from django.core.management.base import BaseCommand
from base.tasks import generate_question_instances_for_all_profiles


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        generate_question_instances_for_all_profiles.delay()


