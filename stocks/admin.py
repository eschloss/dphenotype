from django.contrib import admin
from stocks.models import *
from stocks.tasks import run_subportfolio


def run_position_on_brokerage(modeladmin, request, queryset):
    for q in queryset:
        q.run_position_on_brokerage(logged_in=False)
run_position_on_brokerage.short_description = "Create order on Brokerage"


def try_to_settle(modeladmin, request, queryset):
    for q in queryset:
        q.settle(logged_in=False)
try_to_settle.short_description = "Try to settle the position"


class PositionAdmin(admin.ModelAdmin):
    list_display = ('subportfolio', 'symbol', 'current_quantity', 'goal_percentage', 'agg_total', 'placed_on_brokerage', 'settled', 'sold')
    actions = (run_position_on_brokerage, try_to_settle, )


def run_strategy(modeladmin, request, queryset):
   for q in queryset:
       run_subportfolio(q.pk)
run_strategy.short_description = "Run Portfolio Strategy"


class SubPortfolioAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'userportfolio', 'strategy',)
    actions = (run_strategy, )

    def save_model(self, request, obj, form, change):
        super(SubPortfolioAdmin, self).save_model(request, obj, form, change)
        obj.reset_agg_pc_of_total()


class CashAtDayStartAdmin(admin.ModelAdmin):
    list_display = ('userportfolio', 'total', 'agg_last_run')


admin.site.register(UserPortfolio)
admin.site.register(SubPortfolio, SubPortfolioAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(TransactionLog)
admin.site.register(CashAtDayStart, CashAtDayStartAdmin)
