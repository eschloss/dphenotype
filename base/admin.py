from django.contrib import admin
from base.models import *


class QuestionSectionAdmin(admin.ModelAdmin):
    list_display = ('text', 'order',)
    list_filter = ()


class QuestionGroupAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_section', 'order',)
    list_filter = ()


class QuestionInstanceAdmin(admin.ModelAdmin):
    list_display = ('profile', 'question_template', 'created', 'answered')
    list_filter = ()


admin.site.register(Profile)
admin.site.register(Emoji)
admin.site.register(QuestionSection, QuestionSectionAdmin)
admin.site.register(QuestionGroup, QuestionGroupAdmin)
admin.site.register(MultipleChoiceQuestionTemplate)
admin.site.register(NumberQuestionTemplate)
admin.site.register(FreeTextQuestionTemplate)
admin.site.register(MultipleChoiceQuestionInstance, QuestionInstanceAdmin)
admin.site.register(NumberQuestionInstance, QuestionInstanceAdmin)
admin.site.register(FreeTextQuestionInstance, QuestionInstanceAdmin)

