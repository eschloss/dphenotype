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
    list_display = ('__unicode__', 'symbol', 'current_quantity', 'goal_percentage',
                    'settled_percentage', 'agg_total', 'last_edit_date', 'placed_on_brokerage', 'settled', 'sold',)
    list_filter = ('sold', 'settled', 'placed_on_brokerage',)
    actions = (run_position_on_brokerage, try_to_settle, )


def run_strategy(modeladmin, request, queryset):
   for q in queryset:
       run_subportfolio(q.pk)
run_strategy.short_description = "Run Portfolio Strategy"


def reset_blocked_cash(modeladmin, request, queryset):
    for q in queryset:
       q.get_blocked_cash()
reset_blocked_cash.short_description = "Reset Blocked Cash"


class SubPortfolioAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'userportfolio', 'strategy', 'agg_total', 'agg_last_run')
    actions = (run_strategy, reset_blocked_cash, )

    def save_model(self, request, obj, form, change):
        super(SubPortfolioAdmin, self).save_model(request, obj, form, change)
        obj.reset_agg_pc_of_total()


class CashAtDayStartAdmin(admin.ModelAdmin):
    list_display = ('userportfolio', 'total', 'agg_last_run')


class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ('subportfolio', 'symbol', 'quantity', 'date', 'order_id')


class TotalLogAdmin(admin.ModelAdmin):
    list_display = ('subportfolio', 'date', 'total')
    list_filter = ('subportfolio', 'date')


admin.site.register(UserPortfolio)
admin.site.register(SubPortfolio, SubPortfolioAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(TransactionLog, TransactionLogAdmin)
admin.site.register(CashAtDayStart, CashAtDayStartAdmin)
admin.site.register(TotalLog, TotalLogAdmin)
