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


class Profile(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_id

    def save(self, *args, **kwargs):
        about_to_add = self._state.adding
        super().save(*args, **kwargs)

        if about_to_add:
            #generate baseline Questions
            question_sections = QuestionSection.objects.filter(is_baseline=True, is_dependent_on_question=False)
            for section in question_sections:
                question_groups = section.questiongroup_set.all()
                for group in question_groups:
                    #create multiple choice question instances
                    question_templates = group.multiplechoicequestiontemplate_set.all()
                    for question_template in question_templates:
                        qi = MultipleChoiceQuestionInstance(profile=self, question_template=question_template)
                        qi.save()

                    #create number question instances
                    question_templates = group.numberquestiontemplate_set.all()
                    for question_template in question_templates:
                        qi = NumberQuestionInstance(profile=self, question_template=question_template)
                        qi.save()

                    #create free text question instances
                    question_templates = group.freetextquestiontemplate_set.all()
                    for question_template in question_templates:
                        qi = FreeTextQuestionInstance(profile=self, question_template=question_template)
                        qi.save()


class Emoji(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=2, choices=EMOJI_CHOICES)
    created = models.DateTimeField(auto_now_add=True)


class QuestionSection(models.Model):
    text = models.TextField()
    order = models.IntegerField(default=0)
    is_baseline = models.BooleanField(default=True, help_text="Is this section part of a baseline questionnaire?")
    is_dependent_on_question = models.BooleanField(default=False, help_text="Is this section dependent on the answer to a specific question?")
    dependent_question = models.ForeignKey("MultipleChoiceQuestionTemplate", blank=True, null=True, help_text="Choose the dependent question", on_delete=models.PROTECT)
    dependent_question_answers = models.CharField(max_length=100, blank=True, null=True, help_text="Choose the answer(s) necessary for the dependent quesiton in order to show this question. Separate multiple acceptable answers with a comma.")

    def __str__(self):
        return self.text


class QuestionGroup(models.Model):
    question_section = models.ForeignKey("QuestionSection", blank=True, null=True, on_delete=models.PROTECT)
    text = models.TextField()
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.text


class QuestionTemplate(models.Model):
    text = models.TextField(blank=True)
    question_group = models.ForeignKey("QuestionGroup", blank=True, null=True, on_delete=models.PROTECT)
    order = models.IntegerField(default=0)
    one_time_only = models.BooleanField(default=True)
    frequency_interval = models.IntegerField(default=1440, blank=True, null=True, help_text="Minutes between the next time the question is asked. (only fill-in for routine questions)")

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

    class Meta:
        abstract = True


class MultipleChoiceQuestionInstance(QuestionInstance):
    question_template = models.ForeignKey(MultipleChoiceQuestionTemplate, on_delete=models.PROTECT)
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
    question_template = models.ForeignKey(NumberQuestionTemplate, on_delete=models.PROTECT)
    value = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "%s - %s - %s" % (str(self.profile), str(self.created), str(self.question_template))


class FreeTextQuestionInstance(QuestionInstance):
    question_template = models.ForeignKey(FreeTextQuestionTemplate, on_delete=models.PROTECT)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s - %s - %s" % (str(self.profile), str(self.created), str(self.question_template))
