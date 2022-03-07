from django.db import models
from django.db.models import Sum
import datetime
import math
from base.eastern_time import EST5EDT
from decimal import Decimal
from celery import shared_task


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
    pm = models.FloatField(default=20, help_text="Military time in US Eastern time")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user_id

    def save(self, *args, **kwargs):
        about_to_add = self._state.adding
        super().save(*args, **kwargs)

        generate_question_instances.delay(self.pk)


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
    frequency_time = models.CharField(choices=TIMES_CHOICES, blank=True, null=True, max_length=1)
    threshold = models.TextField(default="", help_text="comma separated list of threshold triggering words", blank=True, null=True)
    send_notification = models.BooleanField(default=False, help_text="does a notification go out for this particular question?")
    who_receives = models.CharField(choices=QUESTION_AUDIENCE_TYPE, max_length=1)
    always_available = models.BooleanField(default=False, help_text="Does a new Instance get created right after the instance is answered?")
    is_dependent_on_question = models.BooleanField(default=False, help_text="Is this section dependent on the answer to other questions?")
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

    class Meta:
        abstract = True


class MultipleChoiceQuestionInstance(QuestionInstance):
    question_template = models.ForeignKey(MultipleChoiceQuestionTemplate, on_delete=models.CASCADE)
    value = models.IntegerField(blank=True, null=True)
    other_value = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "%s - %s - %s" % (str(self.profile), str(self.created), str(self.question_template))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        dependentSections = QuestionSection.objects.filter(is_baseline=True, is_dependent_on_question=True, dependent_question=self.question_template)
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

class PassiveData(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    data = models.JSONField()
    type = models.CharField(max_length=30)
    time = models.DateTimeField(blank=True, null=True) #time of data measurement
    unique_id = models.CharField(max_length=40)
    added = models.DateTimeField(auto_now_add=True)

def create_question_instance_if_needed(profile, questionTemplate, QuestionInstanceModel):
    save_new_instance = False
    now = datetime.datetime.now(tz=EST5EDT())
    last_questioninstance = QuestionInstanceModel.objects.filter(profile=profile, question_template=questionTemplate).order_by('-created')
    if len(last_questioninstance) == 0:
        if now > profile.created + datetime.timedelta(days=questionTemplate.start_days) - datetime.timedelta(hours=2):
            save_new_instance = True
    else:
        if not questionTemplate.one_time_only:
            last_questioninstance = last_questioninstance[0]
            if last_questioninstance.value and questionTemplate.frequency_days and now > last_questioninstance.created + datetime.timedelta(days=questionTemplate.frequency_days) - datetime.timedelta(hours=2):
                save_new_instance = True

    if save_new_instance:
        new_questioninstance = QuestionInstanceModel(profile=profile, question_template=questionTemplate)
        new_questioninstance.save()

@shared_task
def generate_question_instances(pk):
    profile = Profile.objects.get(pk=pk)

    for mct in MultipleChoiceQuestionTemplate.objects.all().remove(question_group__question_section__is_dependent_on_section=True):
        create_question_instance_if_needed(profile, mct, MultipleChoiceQuestionInstance)
    for ftt in FreeTextQuestionTemplate.objects.all().remove(question_group__question_section__is_dependent_on_section=True):
        create_question_instance_if_needed(profile, ftt, FreeTextQuestionInstance)
    for nt in NumberQuestionTemplate.objects.all().remove(question_group__question_section__is_dependent_on_section=True):
        create_question_instance_if_needed(profile, nt, NumberQuestionInstance)
