from django.contrib import admin
from base.models import *


class QuestionSectionAdmin(admin.ModelAdmin):
    list_display = ('section_name', 'order',)
    list_filter = ()

class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'question_section', 'order',)
    list_filter = ()

class QuestionInstanceAdmin(admin.ModelAdmin):
    list_display = ('profile', 'question_template', 'created', 'answered')
    list_filter = (("value", admin.EmptyFieldListFilter), 'profile', 'question_template')

def send_notification(modeladmin, request, queryset):
    for q in queryset:
        send_push_notification(q.pk, PushType.XM, "test notification")
send_notification.short_description = "Send Notification"

class ExpoPushTokenAdmin(admin.ModelAdmin):
    list_display = ('profile', 'token')
    actions = ()

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'last_am_push')
    actions = (send_notification,)

class EmojiAdmin(admin.ModelAdmin):
    list_display = ('profile', 'emoji', 'created',)


class ValidStudyIDAdmin(admin.ModelAdmin):
    list_display = ('study_id',)

class PassiveDataAdmin(admin.ModelAdmin):
    list_display = ('profile', 'type', 'time', 'unique_id', 'added')
    list_filter = ('type', 'profile',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Emoji, EmojiAdmin)
admin.site.register(QuestionSection, QuestionSectionAdmin)
admin.site.register(QuestionGroup, QuestionGroupAdmin)
admin.site.register(MultipleChoiceQuestionTemplate)
admin.site.register(NumberQuestionTemplate)
admin.site.register(FreeTextQuestionTemplate)
admin.site.register(MultipleChoiceQuestionInstance, QuestionInstanceAdmin)
admin.site.register(NumberQuestionInstance, QuestionInstanceAdmin)
admin.site.register(FreeTextQuestionInstance, QuestionInstanceAdmin)
#admin.site.register(ExpoPushToken, ExpoPushTokenAdmin)
admin.site.register(ValidStudyID, ValidStudyIDAdmin)
admin.site.register(PassiveData, PassiveDataAdmin)

