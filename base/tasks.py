import datetime
import logging
from base.eastern_time import EST5EDT
from celery import shared_task
from base.models import *
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from enum import Enum
from requests.exceptions import ConnectionError, HTTPError
import json, re, datetime, logging, base64, requests
from django.shortcuts import get_object_or_404


@shared_task
def generate_question_instances_for_all_profiles():
    now = datetime.datetime.now(tz=EST5EDT())
    hours_ago_1 = now - datetime.timedelta(hours=1)

    profiles = Profile.objects.filter(is_active=True, last_generated__lte=hours_ago_1)
    for p in profiles:
        generate_question_instances.delay(p.pk)

class PushType(Enum):
    AM = 1
    PM = 2

@shared_task
def send_push_notification(pk, push_type: PushType, message):
    profile = get_object_or_404(Profile, pk=pk)
    token = ExpoPushToken.objects.filter(profile=profile)
    if len(token) > 0:
        now = datetime.datetime.now(tz=EST5EDT())
        six_hours_ago = now - datetime.timedelta(hours=6)
        hour = now.hour + now.minute / 60

        match push_type:
            case PushType.AM:
                if profile.last_am_push < six_hours_ago and hour > profile.am:
                    send_push_message(token[0].token, message, profile, now, push_type)
            case PushType.PM:
                if profile.last_pm_push < six_hours_ago and hour > profile.pm:
                    send_push_message(token[0].token, message, profile, now, push_type)

DAILY_NOTIFICATION_MESSAGE = "How are you feeling today?"

@shared_task
def send_daily_push_notifications():
    now = datetime.datetime.now(tz=EST5EDT())
    hours_ago_23 = now - datetime.timedelta(hours=23)
    hour = now.hour + now.minute / 60

    profiles = Profile.objects.filter(is_active=True, last_am_push__lte=hours_ago_23, am__lte=hour)
    for p in profiles:
        send_push_notification.delay(p.pk, PushType.AM, DAILY_NOTIFICATION_MESSAGE)

# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
def send_push_message(token, message, profile, now, push_type: PushType, extra=None):
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        body=message,
                        data=extra))
        match push_type:
            case PushType.AM:
                profile.last_am_push = now
            case PushType.PM:
                profile.last_pm_push = now
        profile.save()
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'errors': exc.errors,
                'response_data': exc.response_data,
            })
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        rollbar.report_exc_info(
            extra_data={'token': token, 'message': message, 'extra': extra})
        raise self.retry(exc=exc)

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        ExpoPushToken.objects.filter(token=token).update(active=False)
    except PushTicketError as exc:
        # Encountered some other per-notification error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'push_response': exc.push_response._asdict(),
            })
        raise self.retry(exc=exc)

