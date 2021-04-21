from django.http import HttpResponse
from base.models import *
import json, re


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
        if type == "multiple_choice":
            mc_list = []
            if template.multiple_choice1:
                mc_list.append({"id": "1", "text": template.multiple_choice1, "pid": qi.pk})
            if template.multiple_choice2:
                mc_list.append({"id": "2", "text": template.multiple_choice2, "pid": qi.pk})
            if template.multiple_choice3:
                mc_list.append({"id": "3", "text": template.multiple_choice3, "pid": qi.pk})
            if template.multiple_choice4:
                mc_list.append({"id": "4", "text": template.multiple_choice4, "pid": qi.pk})
            if template.multiple_choice5:
                mc_list.append({"id": "5", "text": template.multiple_choice5, "pid": qi.pk})
            if template.multiple_choice6:
                mc_list.append({"id": "6", "text": template.multiple_choice6, "pid": qi.pk})
            if template.multiple_choice7:
                mc_list.append({"id": "7", "text": template.multiple_choice7, "pid": qi.pk})
            if template.multiple_choice8:
                mc_list.append({"id": "8", "text": template.multiple_choice8, "pid": qi.pk})
            if template.multiple_choice9:
                mc_list.append({"id": "9", "text": template.multiple_choice9, "pid": qi.pk})
            if template.multiple_choice10:
                mc_list.append({"id": "10", "text": template.multiple_choice10, "pid": qi.pk})
            if template.multiple_choice11:
                mc_list.append({"id": "11", "text": template.multiple_choice11, "pid": qi.pk})
            if template.multiple_choice12:
                mc_list.append({"id": "12", "text": template.multiple_choice12, "pid": qi.pk})
            question_dict["options"] = mc_list

            if template.include_other_field:
                question_dict["other"] = template.other_field_label if template.other_field_label else "other"
        if type == "numbers":
            question_dict["as_range"] = template.view_as_range
            question_dict["range_min"] = template.range_min
            question_dict["range_max"] = template.range_max
            if template.range_min_label:
                question_dict["range_min_label"] = template.range_min_label
            if template.range_max_label:
                question_dict["range_max_label"] = template.range_max_label

        if template.question_group:
            group = template.question_group
            group_dict = {"text": group.text, "order": group.order, "questions": {}}
            if group.question_section:
                section = group.question_section
                if section.pk not in sections:
                    sections[section.pk] = {"text": section.text, "order": section.order, "groups": {}}

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
        sections, unattached_groups, unattached_questions = add_questions_to_dictionaries(mc_qis, "multiple_choice", {}, {}, {})
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
    data = json.loads(request.body.decode('utf-8'))
    print(data)
    if data.__contains__("user_id"):
        print("user Id detected")
        profile = Profile.objects.get(user_id=data["user_id"])

        for key, val in data['answers'].items():
            if re.search(r'^mc_|^ft_|^n_', key):
                qid = re.search(r'_([^_]*$)', key).group(1)
                answer = val
                if re.search(r'^mc_', key):
                    if val == 'o' and data['answers']['mco_%s' % qid]:
                        answer = data['answers']['mco_%s' % qid]
                elif re.search(r'^ft_', key):
                    pass
                elif re.search(r'^n_', key):
                    pass
                print("%s ---- %s" % (key, answer))

        if request.POST.__contains__("instance_id") and request.POST.__contains__("value") and request.POST.__contains__("type"):
            type = request.POST["type"]
            if type in TYPE_TO_MODEL:
                instance = TYPE_TO_MODEL[type].objects.get(pk=int(request.POST["instance_id"]))
                instance.value = request.POST["value"]
                if request.POST.__contains__("other_value"):
                    instance.other_value = request.POST["other_value"]
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
        date_emojis = sorted(dates.items(), reverse=True, key=lambda a: a[0])

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

        return HttpResponse(json.dumps(full_date_emoji_list), content_type='application/json')
    return HttpResponse(json.dumps({"success": False}), content_type='application/json')


def get_average_emojis(request):
    if request.GET.__contains__("user_id"):
        profile = Profile.objects.get(user_id=request.GET["user_id"])
        now = datetime.datetime.now()
        emojis = Emoji.objects.filter(profile=profile, created__gt=now - datetime.timedelta(days=30)).order_by('-created')
        monthly_emoji_dict = {}
        for emoji in emojis:
            if emoji.emoji in monthly_emoji_dict:
                monthly_emoji_dict[emoji.emoji] += 1
            else:
                monthly_emoji_dict[emoji.emoji] = 1
        monthlyMaxItem = '0'
        max = 0
        for key, item in monthly_emoji_dict.items():
            if item > max:
                monthlyMaxItem = key

        emojis = Emoji.objects.filter(profile=profile, created__gt=now - datetime.timedelta(days=7)).order_by('-created')
        weekly_emoji_dict = {}
        for emoji in emojis:
            if emoji.emoji in weekly_emoji_dict:
                weekly_emoji_dict[emoji.emoji] += 1
            else:
                weekly_emoji_dict[emoji.emoji] = 1
        weeklyMaxItem = '0'
        max = 0
        for key, item in weekly_emoji_dict.items():
            if item > max:
                weeklyMaxItem = key

        return HttpResponse(json.dumps({"weekly": weeklyMaxItem, "monthly": monthlyMaxItem}), content_type='application/json')
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
