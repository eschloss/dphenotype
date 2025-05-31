from django.db import models
from django.db.models import Sum
import datetime
import math
from config.settings import MAILGUN_API_KEY
import os, requests
import random
from base.eastern_time import EST5EDT
from decimal import Decimal
from celery import shared_task
from django.core.mail import send_mail
from config.settings import THRESHOLD_EMAIL
from enum import IntEnum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from requests.exceptions import ConnectionError, HTTPError
import onesignal
from onesignal.api import default_api
from onesignal.model.notification import Notification
from config.settings import ONESIGNAL_APP_KEY, ONESIGNAL_USER_KEY, ONESIGNAL_APP_ID




# Must Match the emojis on the apps
EMOJI_CHOICES = (
    ('0', 'Happy'),
    ('1', 'Unhappy'),
    ('2', 'Sick'),
    ('3', 'Very Ill'),
    ('4', 'Feeling Down'),
    ('5', 'Exhausted'),
    ('6', 'Hopeful'),
    ('7', 'Lonely'),
    ('9', 'Stressed'),
    ('10', 'Relaxed'),
    ('11', 'Agitated'),
    ('12', 'Energetic'),
    ('13', 'Blessed'),
    ('14', 'Hopeless'),
    ('15', 'Angry'),
    ('16', 'Worried'),
    ('17', 'Other'),
    ('18', 'Negative'),
    ('19', 'Neutral'),
    ('20', 'Positive'),
)

ACCOUNT_TYPE = (
    ('y', 'youth'),
    ('c', 'caretaker'),
)
QUESTION_AUDIENCE_TYPE = (
    ('y', 'youth'),
    ('b', 'both youth and caretaker'),
    ('c', 'caregiver ONLY'),
)


class Profile(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=ACCOUNT_TYPE, max_length=1)
    am = models.FloatField(default=8, help_text="Military time in US Eastern time")
    pm = models.FloatField(default=20, help_text="Military time in US Eastern time - must be earlier than 24 (before midnight)")
    next_random = models.FloatField(default=16)
    is_active = models.BooleanField(default=True)
    last_am_push = models.DateTimeField(default=timezone.now)
    last_pm_push = models.DateTimeField(default=timezone.now)
    last_generated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user_id

    def reset_next_random(self):
        self.next_random = random.uniform(self.am, self.pm)
        self.save(generate_questions=False)

    def save(self, *args, generate_questions=True, **kwargs):
        about_to_add = self._state.adding
        super().save(*args, **kwargs)

        if generate_questions:
            generate_question_instances(self.pk)
        if about_to_add:
            generate_question_instances(self.pk)


class Emoji(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=2, choices=EMOJI_CHOICES)
    created = models.DateTimeField(auto_now_add=True)


class QuestionSection(models.Model):
    section_name = models.CharField(max_length=100, help_text="only for internal use")
    text = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_baseline = models.BooleanField(default=False, help_text="Is this section part of a baseline questionnaire?")
    is_static = models.BooleanField(default=False, help_text="Is this section part of the static section?")
    is_dependent_on_question = models.BooleanField(default=False, help_text="Is this section dependent on the answer to a specific question?")
    dependent_question = models.ForeignKey("MultipleChoiceQuestionTemplate", blank=True, null=True, help_text="Choose the dependent question", on_delete=models.CASCADE)
    dependent_question_answers = models.CharField(max_length=100, blank=True, null=True, help_text="Choose the answer(s) necessary for the dependent quesiton in order to show this question. Separate multiple acceptable answers with a comma.")

    def __str__(self):
        return self.section_name


class QuestionGroup(models.Model):
    group_name = models.CharField(max_length=100, help_text="only for internal use")
    question_section = models.ForeignKey("QuestionSection", blank=True, null=True, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    send_notification = models.BooleanField(default=False, help_text="does a notification go out for this particular group?")

    def __str__(self):
        return self.group_name


TIMES_CHOICES = (
    ('a', "AM"),
    ('p', "PM"),
    ('r', "random"),
)


class QuestionTemplate(models.Model):
    text = models.TextField(blank=True)
    question_group = models.ForeignKey("QuestionGroup", blank=True, null=True, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    one_time_only = models.BooleanField(default=False)
    frequency_days = models.IntegerField(default=1, blank=True, null=True, help_text="Days until the next time the question is asked. (leave blank if it's not a routine question).")
    start_days = models.IntegerField(default=0) #days after User joins to first create this question
    frequency_time = models.CharField(choices=TIMES_CHOICES, blank=True, null=True, max_length=1)
    threshold = models.TextField(default="", help_text="comma separated list of threshold triggering words", blank=True, null=True)
    send_notification = models.BooleanField(default=False, help_text="does a notification go out for this particular question?")
    who_receives = models.CharField(choices=QUESTION_AUDIENCE_TYPE, max_length=1)
    always_available = models.BooleanField(default=False, help_text="Does a new Instance get created right after the instance is answered?")
    is_dependent_on_question = models.BooleanField(default=False, help_text="Is this question dependent on the answer to other questions?")
    dependent_question = models.ForeignKey("MultipleChoiceQuestionTemplate", blank=True, null=True, help_text="Choose the dependent question", on_delete=models.CASCADE)
    dependent_question_answers = models.CharField(max_length=100, blank=True, null=True, help_text="Choose the answer(s) necessary for the dependent quesiton in order to show this question. Separate multiple acceptable answers with a comma.")
    """ Note: the dependent questions should be generated always, 
    but just kept hidden within the App until the correct answers are selected.
    There are three types of dependencies:
        1) A whole Question section is dependent on a MultipleChoice Question (fields in QuestionSection model)
        2) Question shows up when any of the MC questions within a QuestionGroup are triggered
            dependent_question is null 
            dependent_question_answers
        3) Question shows up when one specific MC Question is triggered 
            dependent_question is set to something
            dependent_question_answers
    """

    class Meta:
        abstract = True

    def __str__(self):
        if self.question_group:
            return "%s %s" % (str(self.question_group), self.text)
        else:
            return self.text

    def get_notification_text(self):
        if self.question_group:
            return self.question_group.text
        else:
            return self.text

class MultipleChoiceQuestionTemplate(QuestionTemplate):
    multiple_choice1 = models.CharField(max_length=50, blank=True, null=True)
    multiple_choice2 = models.CharField(max_length=50, blank=True, null=True)
    multiple_choice3 = models.CharField(max_length=50, blank=True, null=True)
    multiple_choice4 = models.CharField(max_length=50, blank=True, null=True)
    multiple_choice5 = models.CharField(max_length=50, blank=True, null=True)
    multiple_choice6 = models.CharField(max_length=50, blank=True, null=True)
    multiple_choice7 = models.CharField(max_length=50, blank=True, null=True)
    multiple_choice8 = models.CharField(max_length=50, blank=True, null=True)
    multiple_choice9 = models.CharField(max_length=50, blank=True, null=True)
    multiple_choice10 = models.CharField(max_length=50, blank=True, null=True)
    multiple_choice11 = models.CharField(max_length=50, blank=True, null=True)
    multiple_choice12 = models.CharField(max_length=50, blank=True, null=True)
    include_other_field = models.BooleanField(default=False)
    other_field_label = models.CharField(max_length=50, blank=True, null=True)


class NumberQuestionTemplate(QuestionTemplate):
    view_as_range = models.BooleanField(default=False)
    range_min = models.IntegerField(blank=True, null=True)
    range_max = models.IntegerField(blank=True, null=True)
    range_min_label = models.CharField(max_length=50, blank=True, null=True)
    range_max_label = models.CharField(max_length=50, blank=True, null=True)


class FreeTextQuestionTemplate(QuestionTemplate):
    pass


class QuestionInstance(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    answered = models.DateTimeField(blank=True, null=True)
    notification_count = models.IntegerField(default=0)
    last_notification = models.DateTimeField(blank=True, null=True)
    question_template = None
    value = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.question_template.threshold:
            threshold_options = map(lambda a: a.strip(), self.question_template.threshold.split(","))
            for threshold_option in threshold_options:
                if threshold_option in str(self.value):
                    message = f"participant study id = { self.profile.user_id }\n\n"
                    message += f"Question: { self.question_template }\n"
                    message += f"Question Template ID: { self.question_template.pk }\n"
                    message += f"Question Instance ID: { self.pk }\n"
                    message += f"Answer: { self.value }\n\n"
                    """
                    send_mail(f"Threshold Triggered for Participant {self.profile.user_id}",
                              message, "info@dphenotype.herokuapp.com",
                              [THRESHOLD_EMAIL,], fail_silently=True)
                    """
                    requests.post(
                        "https://api.mailgun.net/v3/sandbox7e7f3635ddb14d70a85e215ec1d80fc2.mailgun.org/messages",
                        auth=("api", MAILGUN_API_KEY), data={
                            "from": "Geomood App <geomood.threshold@dphenotype.herokuapp.com>",
                            "to": THRESHOLD_EMAIL, "subject": f"Threshold Triggered for Participant {self.profile.user_id}",
                            "text": message })


class MultipleChoiceQuestionInstance(QuestionInstance):
    question_template = models.ForeignKey(MultipleChoiceQuestionTemplate, on_delete=models.CASCADE)
    value = models.IntegerField(blank=True, null=True)
    other_value = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "%s - %s - %s" % (str(self.profile), str(self.created), str(self.question_template))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.value:
            dependentSections = QuestionSection.objects.filter(is_dependent_on_question=True, dependent_question=self.question_template)
            for ds in dependentSections:
                answers = map(lambda a: a.strip(), ds.dependent_question_answers.split(","))
                if str(self.value) in answers:
                    question_groups = ds.questiongroup_set.all()
                    for group in question_groups:
                        # create multiple choice question instances
                        question_templates = group.multiplechoicequestiontemplate_set.all()
                        for question_template in question_templates:
                            qi = MultipleChoiceQuestionInstance(profile=self.profile, question_template=question_template)
                            qi.save()

                        # create number question instances
                        question_templates = group.numberquestiontemplate_set.all()
                        for question_template in question_templates:
                            qi = NumberQuestionInstance(profile=self.profile, question_template=question_template)
                            qi.save()

                        # create free text question instances
                        question_templates = group.freetextquestiontemplate_set.all()
                        for question_template in question_templates:
                            qi = FreeTextQuestionInstance(profile=self.profile, question_template=question_template)
                            qi.save()

            """ Note: this isn't necessary because the mobile app keeps dependent questions hidden until they are triggered
            dependentQuestions = MultipleChoiceQuestionTemplate.objects.filter(is_dependent_on_question=True, dependent_question=self.question_template)
            for dq in dependentQuestions:
                answers = map(lambda a: a.strip(), dq.dependent_question_answers.split(","))
                if str(self.value) in answers:
                    qi = MultipleChoiceQuestionInstance(profile=self.profile, question_template=dq)
                    qi.save()
            dependentQuestions = NumberQuestionTemplate.objects.filter(is_dependent_on_question=True, dependent_question=self.question_template)
            for dq in dependentQuestions:
                answers = map(lambda a: a.strip(), dq.dependent_question_answers.split(","))
                if str(self.value) in answers:
                    qi = NumberQuestionInstance(profile=self.profile, question_template=dq)
                    qi.save()
            dependentQuestions = FreeTextQuestionTemplate.objects.filter(is_dependent_on_question=True, dependent_question=self.question_template)
            for dq in dependentQuestions:
                answers = map(lambda a: a.strip(), dq.dependent_question_answers.split(","))
                if str(self.value) in answers:
                    qi = FreeTextQuestionInstance(profile=self.profile, question_template=dq)
                    qi.save()
            """




class NumberQuestionInstance(QuestionInstance):
    question_template = models.ForeignKey(NumberQuestionTemplate, on_delete=models.CASCADE)
    value = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "%s - %s - %s" % (str(self.profile), str(self.created), str(self.question_template))


class FreeTextQuestionInstance(QuestionInstance):
    question_template = models.ForeignKey(FreeTextQuestionTemplate, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s - %s - %s" % (str(self.profile), str(self.created), str(self.question_template))

class ExpoPushToken(models.Model):
    token = models.CharField(max_length=60)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

class ValidStudyID(models.Model):
    study_id = models.CharField(max_length=60)
    type = models.CharField(choices=ACCOUNT_TYPE, max_length=1, default='y')

class PassiveData(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    data = models.JSONField()
    type = models.CharField(max_length=30)
    time = models.DateTimeField(blank=True, null=True) #time of data measurement
    unique_id = models.CharField(max_length=40)
    added = models.DateTimeField(auto_now_add=True)

def create_question_instance_if_needed(profile, questionTemplate, QuestionInstanceModel, now=datetime.datetime.now(tz=EST5EDT())):
    save_new_instance = False
    six_hours_ago = now - datetime.timedelta(hours=6)
    hour = now.hour + now.minute / 60
    last_questioninstance = QuestionInstanceModel.objects.filter(profile=profile, question_template=questionTemplate).order_by('-created')
    send_notification = False

    if last_questioninstance.count() == 0:
        if questionTemplate.start_days == 0 or now > profile.created + datetime.timedelta(days=questionTemplate.start_days) - datetime.timedelta(hours=2): #start_days
            """if (not questionTemplate.frequency_time or \
                questionTemplate.frequency_time == 'a' and hour > profile.am or \
                questionTemplate.frequency_time == 'p' and hour > profile.pm or \
                questionTemplate.frequency_time == 'r' and hour > profile.next_random):"""
            save_new_instance = True

    else:
        if not questionTemplate.one_time_only:
            last_questioninstance = last_questioninstance[0]
            if questionTemplate.frequency_days and now > last_questioninstance.created + datetime.timedelta(days=questionTemplate.frequency_days) - datetime.timedelta(hours=2):
                if last_questioninstance.value and now > last_questioninstance.answered + datetime.timedelta(hours=23):
                    """if (not questionTemplate.frequency_time or \
                        questionTemplate.frequency_time == 'a' and hour > profile.am or \
                        questionTemplate.frequency_time == 'p' and hour > profile.pm or \
                        questionTemplate.frequency_time == 'r' and hour > profile.next_random):"""
                    save_new_instance = True

                if questionTemplate.send_notification and \
                        not save_new_instance and not last_questioninstance.value and \
                        (questionTemplate.frequency_time == 'a' and profile.last_am_push < six_hours_ago and hour >= profile.am or \
                        questionTemplate.frequency_time == 'p' and profile.last_pm_push < six_hours_ago and hour >= profile.pm):
                    send_notification = True

    if save_new_instance:
        send_notification = questionTemplate.send_notification
        new_questioninstance = QuestionInstanceModel(profile=profile, question_template=questionTemplate)
        new_questioninstance.save()

        if questionTemplate.frequency_time == 'r':
            profile.reset_next_random()

    if send_notification:
        if questionTemplate.frequency_time == 'a':
            send_push_notification(profile.pk, int(PushType.AM), questionTemplate.get_notification_text())
        elif questionTemplate.frequency_time == 'p':
            send_push_notification(profile.pk, int(PushType.PM), questionTemplate.get_notification_text())

@shared_task
def generate_question_instances(pk):
    profile = Profile.objects.get(pk=pk)

    for mct in MultipleChoiceQuestionTemplate.objects \
            .filter(who_receives__in=('b', profile.type)) \
            .exclude(question_group__question_section__is_dependent_on_question=True):
        create_question_instance_if_needed(profile, mct, MultipleChoiceQuestionInstance)
    for ftt in FreeTextQuestionTemplate.objects \
            .filter(who_receives__in=('b', profile.type)) \
            .exclude(question_group__question_section__is_dependent_on_question=True):
        create_question_instance_if_needed(profile, ftt, FreeTextQuestionInstance)
    for nt in NumberQuestionTemplate.objects \
            .filter(who_receives__in=('b', profile.type)) \
            .exclude(question_group__question_section__is_dependent_on_question=True):
        create_question_instance_if_needed(profile, nt, NumberQuestionInstance)

    now = datetime.datetime.now(tz=EST5EDT())
    profile.last_generated = now
    profile.save(generate_questions=False)

class PushType(IntEnum):
    AM = 1
    PM = 2
    XM = 3

@shared_task
def send_push_notification(pk, push_type, message):
    profile = get_object_or_404(Profile, pk=pk)
    token = ExpoPushToken.objects.filter(profile=profile)
    if len(token) == 0:
        token = None
    else:
        token = token[0].token

    now = datetime.datetime.now(tz=EST5EDT())
    six_hours_ago = now - datetime.timedelta(hours=6)
    hour = now.hour + now.minute / 60

    if push_type == PushType.AM:
        if profile.last_am_push < six_hours_ago and hour >= profile.am:
            send_push_message(token, message, profile, now, push_type)
    elif push_type == PushType.PM:
        if profile.last_pm_push < six_hours_ago and hour >= profile.pm:
            send_push_message(token, message, profile, now, push_type)
    elif push_type == PushType.XM:
        send_push_message(token, message, profile, now, push_type)



def send_onesignal_push_notification_task(external_id, en_title="title", en_body="body"):
        configuration = onesignal.Configuration(
            app_key=ONESIGNAL_APP_KEY,
            user_key=ONESIGNAL_USER_KEY
        )

        with onesignal.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = default_api.DefaultApi(api_client)

            notification = Notification(
                app_id=ONESIGNAL_APP_ID,
                include_external_user_ids=[external_id],
                contents={
                    "en": en_body,
                },
                headings={
                    "en": en_title,
                },
            )

            try:
                # Create notification
                api_response = api_instance.create_notification(notification)
                return True
            except onesignal.ApiException as e:
                return False

# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
def send_push_message(token, message, profile, now, push_type, extra=None):
    try:
        send_onesignal_push_notification_task(profile.user_id, en_title=message, en_body=message)

        if push_type == PushType.AM:
            profile.last_am_push = now
        elif push_type == PushType.PM:
            profile.last_pm_push = now
        profile.save(generate_questions=False)
    except:
        pass

    if token:
        try:
            response = PushClient().publish(
                PushMessage(to=token,
                            body=message,
                            data=extra))
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

        if push_type == PushType.AM:
            profile.last_am_push = now
        elif push_type == PushType.PM:
            profile.last_pm_push = now
        profile.save(generate_questions=False)

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
