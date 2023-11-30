import datetime
import logging
from base.eastern_time import EST5EDT
from celery import shared_task
from base.models import Profile, send_push_notification, PushType, generate_question_instances
from requests.exceptions import ConnectionError, HTTPError
import json, re, datetime, logging, base64, requests


@shared_task
def generate_question_instances_for_all_profiles():
    now = datetime.datetime.now(tz=EST5EDT())
    min_time_interval = now - datetime.timedelta(minutes=15)

    profiles = Profile.objects.filter(is_active=True, last_generated__lte=min_time_interval)
    for p in profiles:
        #generate_question_instances.delay(p.pk)
        generate_question_instances(p.pk)

DAILY_NOTIFICATION_MESSAGE = "How are you feeling?"

@shared_task
def send_daily_push_notifications():
    now = datetime.datetime.now(tz=EST5EDT())
    hours_ago_23 = now - datetime.timedelta(hours=23)
    hour = now.hour + now.minute / 60

    profiles = Profile.objects.filter(is_active=True, last_am_push__lte=hours_ago_23, am__lte=hour)
    for p in profiles:
        #send_push_notification.delay(p.pk, int(PushType.AM), DAILY_NOTIFICATION_MESSAGE)
        send_push_notification(p.pk, int(PushType.AM), DAILY_NOTIFICATION_MESSAGE)

@shared_task
def send_push_notifications():
    profiles = Profile.objects.filter(is_active=True)
    for p in profiles:
        send_push_notification(p.pk, int(PushType.AM), DAILY_NOTIFICATION_MESSAGE)


