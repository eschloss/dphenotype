import datetime
import logging
from base.eastern_time import EST5EDT
from celery import shared_task
from base.models import *


@shared_task
def generate_question_instances(pk):
    profile = Profile.objects.get(pk=pk)
    #TODO add dependent question sections in
    #TODO add recurring questions in


@shared_task
def generate_question_instances_for_all_profiles():
    profiles = Profile.objects.all()
    for p in profiles:
        generate_question_instances.delay(p.pk)

