from django.http import HttpResponse
from base.models import *
import json


def home(request):
    response = ""
    response += "Hello World<br/>"

    return HttpResponse(response)


def login(request):
    if request.GET.__contains__("user_id"):
        profile, is_new = Profile.objects.get_or_create(user_id=request.GET["user_id"])
        return HttpResponse(json.dumps({"success": True, "is_new": is_new }), content_type='application/json')
    return HttpResponse(json.dumps({"success": False}), content_type='application/json')


def add_questions_to_dictionaries(questions_instances, type, sections={}, unattached_groups={}, unattached_questions={}):
    for qi in questions_instances:
        template = qi.question_template
        question_dict = {"instance_id": qi.pk, "text": template.text, "order": template.order, "type": type}
        if template.question_group:
            group = template.question_group
            group_dict = {"text": group.text, "order": group.order}
            group_dict["questions"] = {}
            if group.question_section:
                section = group.question_section
                if section.pk not in sections:
                    sections[section.pk] = {"text": section.text, "order": section.order,}
                    sections[section.pk]["groups"] = {}
                #if len(sections[section.pk]["groups"]) == 0:  # some strange bug so i added this if statement
                #    sections[section.pk]["groups"][group.pk] = {}
                if group.pk not in sections[section.pk]["groups"]:
                    sections[section.pk]["groups"][group.pk] = group_dict
                if template.pk not in sections[section.pk]["groups"][group.pk]["questions"]:
                    sections[section.pk]["groups"][group.pk]["questions"][template.pk] = question_dict
            else:
                if group.pk not in unattached_groups:
                    unattached_groups[group.pk] = group_dict
                if template.pk not in unattached_groups[group.pk]["questions"]:
                    unattached_groups[group.pk]["questions"][template.pk] = question_dict
        else:
            if template.pk not in unattached_questions:
                unattached_questions[template.pk] = question_dict
    return sections, unattached_groups, unattached_questions


def order_questions_dicts(sections, groups, questions):
    questions = sorted(questions.items(), key=lambda a: a[1]["order"])

    groups = groups.items()
    for group_key, group in groups:
        group["questions"] = sorted(group["questions"].items(), key=lambda a: a[1]["order"])
    groups = sorted(groups, key=lambda a: a[1]["order"])

    sections = sections.items()
    for section_key, section in sections:
        section["groups"] = section["groups"].items()
        for group_key, group in section["groups"]:
            group["questions"] = sorted(group["questions"].items(), key=lambda a: a[1]["order"])
        section["groups"] = sorted(section["groups"], key=lambda a: a[1]["order"])
    sections = sorted(sections, key=lambda a: a[1]["order"])

    return {"sections": sections, "groups": groups, "questions": questions}


# this is called when a user goes to the Questions page
def gather_question_instances(request):
    if request.GET.__contains__("user_id"):
        profile = Profile.objects.get(user_id=request.GET["user_id"])
        mc_qis = MultipleChoiceQuestionInstance.objects.filter(profile=profile, answered__isnull=True)
        n_qis = NumberQuestionInstance.objects.filter(profile=profile, answered__isnull=True)
        ft_qis = FreeTextQuestionInstance.objects.filter(profile=profile, answered__isnull=True)
        sections, unattached_groups, unattached_questions = add_questions_to_dictionaries(mc_qis, "multiple_choice")
        sections, unattached_groups, unattached_questions = add_questions_to_dictionaries(n_qis, "numbers", sections, unattached_groups, unattached_questions)
        sections, unattached_groups, unattached_questions = add_questions_to_dictionaries(ft_qis, "free_text", sections, unattached_groups, unattached_questions)
        response = order_questions_dicts(sections, unattached_groups, unattached_questions)
        return HttpResponse(json.dumps(response), content_type='application/json')
    return HttpResponse(json.dumps({"success": False}), content_type='application/json')


TYPE_TO_MODEL = {
    "multiple_choice": MultipleChoiceQuestionInstance,
    "free_text": FreeTextQuestionInstance,
    "number": NumberQuestionInstance,
}


# this is called when a user answers a question
def set_question_instance(request):
    if request.GET.__contains__("user_id"):
        profile = Profile.objects.get(user_id=request.GET["user_id"])
        if request.GET.__contains__("instance_id") and request.GET.__contains__("value") and request.GET.__contains__("type"):
            type = request.GET["type"]
            if type in TYPE_TO_MODEL:
                instance = TYPE_TO_MODEL[type].objects.get(pk=int(request.GET["instance_id"]))
                instance.value = request.GET["value"]
                if request.GET.__contains__("other_value"):
                    instance.other_value = request.GET["other_value"]
                instance.answered = datetime.datetime.now()
                instance.save()
                return HttpResponse(json.dumps({"success": True}), content_type='application/json')
    return HttpResponse(json.dumps({"success": False}), content_type='application/json')


def get_past_emojis(request):
    if request.GET.__contains__("user_id"):
        profile = Profile.objects.get(user_id=request.GET["user_id"])
        now = datetime.datetime.now()
        emojis = Emoji.objects.filter(profile=profile, created__gt=now - datetime.timedelta(days=30)).order_by('-created')
        dates = {}
        for emoji in emojis:
            if emoji.created.date() not in dates:
                dates[emoji.created.date()] = emoji.emoji
        date_emojis = sorted(dates.items(), key=lambda a: a[0])

        full_date_emoji_list = []
        today = now.date()
        counter = 0
        for date_emoji in date_emojis:
            while counter < (today - date_emoji[0]).days:
                full_date_emoji_list.append((counter, "none"))
                counter += 1
            full_date_emoji_list.append((counter, date_emoji[1]))
            counter += 1

        while counter < 30:
            full_date_emoji_list.append((counter, "none"))
            counter += 1

        print(full_date_emoji_list)

        return HttpResponse(json.dumps(full_date_emoji_list), content_type='application/json')
    return HttpResponse(json.dumps({"success": False}), content_type='application/json')


def set_emoji(request):
    if request.GET.__contains__("user_id"):
        profile = Profile.objects.get(user_id=request.GET["user_id"])
        if request.GET.__contains__("emoji"):
            try:
                emoji = Emoji.objects.filter(profile=profile, created__gt=datetime.datetime.now() - datetime.timedelta(minutes=3))
                emoji = emoji[0]
            except:
                emoji = Emoji(profile=profile)
            emoji.emoji = request.GET["emoji"]
            emoji.save()
            return HttpResponse(json.dumps({"success": True}), content_type='application/json')
    return HttpResponse(json.dumps({"success": False}), content_type='application/json')
