from django.db import models
from django.db.models import Sum
import datetime
from stocks.rh_utils import trading_login, get_available_cash, get_stock_values_by_symbol_list, get_order_info, fractional_order
from stocks.eastern_time import EST5EDT
from decimal import Decimal
from celery import shared_task

LAUNCH_DATETIME = datetime.datetime(2014, 9, 12, 11, 19, 54)


class UserPortfolio(models.Model):
    name = models.CharField(max_length=50)
    on = models.BooleanField(default=True)
    account_id = models.CharField(max_length=12)

    def __unicode__(self):
        return "%s: %s" % (str(self.pk), self.name)


class CashAtDayStart(models.Model):
    userportfolio = models.ForeignKey(UserPortfolio, on_delete=models.PROTECT)
    total = models.DecimalField(decimal_places=8, max_digits=16, default=0)
    agg_last_run = models.DateTimeField(default=LAUNCH_DATETIME)

    def reset(self, logged_in=False):
        if not logged_in:
            trading_login()

        now = datetime.datetime.now(tz=EST5EDT())
        if now.date() != self.agg_last_run.date():
            self.agg_last_run = now
            self.total = get_available_cash()
            self.save()

            self.userportfolio.subportfolio_set.all().update(blocked_cash=0)



STRATEGIES = [
    {
        "CODE": "0",
        "NAME": "Sector Strategy 1",
        "DESCRIPTION": "Takes the worst performing sectors that used to be performing well and buys them.",
    },
    {
        "CODE": "1",
        "NAME": "Keep as Cash",
        "DESCRIPTION": "Sells everything and keeps as cash",
    },
    {
        "CODE": "2",
        "NAME": "Put into VTI",
        "DESCRIPTION": "Puts everything into VTI",
    },
]
STRATEGY_CHOICES = list(map(lambda a: (a['CODE'], a['NAME']), STRATEGIES))


class SubPortfolio(models.Model):
    name = models.CharField(blank=True, null=True, max_length=200)
    userportfolio = models.ForeignKey(UserPortfolio, on_delete=models.PROTECT)
    strategy = models.CharField(max_length=3, choices=STRATEGY_CHOICES)
    points = models.IntegerField(default=1)  # how many points does this strategy get relative to other subportfolios strategies
    notes = models.TextField(blank=True, null=True)
    run_hour = models.FloatField(default=.95)  # as percent of trading day.
    is_being_run_currently_lock = models.BooleanField(default=False)
    agg_pc_of_total = models.FloatField(default=1)  # what pc of user's new investments should go into this subportfolios
    agg_last_run = models.DateTimeField(default=LAUNCH_DATETIME)
    agg_total = models.DecimalField(decimal_places=8, max_digits=16, default=0)
    agg_total_last_set = models.DateTimeField(default=LAUNCH_DATETIME)
    blocked_cash = models.DecimalField(decimal_places=8, max_digits=16, default=0)

    def __unicode__(self):
        return "%s: %s" % (str(self.pk), self.name)

    def reset_agg_pc_of_total(self, recursion=True):
        agg_pc_of_total = float(self.points) / float(SubPortfolio.objects.filter(userportfolio=self.userportfolio).aggregate(Sum('points'))['points__sum'])
        print(agg_pc_of_total)
        if self.agg_pc_of_total != agg_pc_of_total:
            self.agg_pc_of_total = agg_pc_of_total
            self.save()
            if recursion:
                for sp in SubPortfolio.objects.filter(userportfolio=self.userportfolio):
                    sp.reset_agg_pc_of_total(recursion=False)

    def get_allocated_cash_for_new_investments(self, logged_in=False):
        cash, created = CashAtDayStart.objects.get_or_create(userportfolio=self.userportfolio)
        sportfolios = self.userportfolio.subportfolio_set.all()
        total_points = sportfolios.aggregate(Sum('points'))['points__sum']
        return cash.total * self.points / Decimal(total_points)

    def set_total(self, logged_in=False):
        if not logged_in:
            trading_login()

        now = datetime.datetime.now(tz=EST5EDT())
        positions = Position.objects.filter(subportfolio=self, sold=False, current_quantity__gt=0)
        symbol_list = list(map(lambda a: a.symbol, list(positions)))
        total = 0

        if len(symbol_list) > 0:
            value_list = get_stock_values_by_symbol_list(symbol_list)

            for position in positions:
                val = value_list.pop(0)
                position.agg_total = val * position.current_quantity
                position.agg_total_last_set = now
                position.save()
                total += position.agg_total

        self.agg_total = total
        self.agg_total_last_set = now
        self.save()

    def get_total(self, logged_in=False):
        if self.agg_total_last_set < datetime.datetime.now(tz=EST5EDT()) - datetime.timedelta(minutes=5):
            if not logged_in:
                trading_login()
            self.set_total(logged_in=True)
        return self.agg_total


@shared_task
def queue_run_position_on_brokerage(pk):
    position = Position.objects.get(pk=pk)
    position.run_position_on_brokerage()


@shared_task
def queue_check_position_on_brokerage(pk):
    position = Position.objects.get(pk=pk)
    position.settle()


class Position(models.Model):
    subportfolio = models.ForeignKey(SubPortfolio, on_delete=models.PROTECT)
    symbol = models.CharField(max_length=15)
    current_quantity = models.DecimalField(decimal_places=8, max_digits=16, default=0)
    settled_percentage = models.DecimalField(decimal_places=8, max_digits=9, default=0)
    goal_percentage = models.DecimalField(decimal_places=8, max_digits=9)
    first_transaction_date = models.DateTimeField(auto_now_add=True)
    last_edit_date = models.DateTimeField(auto_now=True)
    sold = models.BooleanField(default=False)
    placed_on_brokerage = models.BooleanField(default=False)
    settled = models.BooleanField(default=False)
    latest_order_id = models.CharField(max_length=50, blank=True, null=True)
    position_id = models.URLField(blank=True, null=True)  # this url may include multiple positions if the same stock is used in multiple portfolios
    instrument_id = models.URLField(blank=True, null=True)
    agg_total = models.DecimalField(decimal_places=8, max_digits=16, default=0)
    agg_total_last_set = models.DateTimeField(default=LAUNCH_DATETIME)
    amount_blocked = models.DecimalField(decimal_places=8, max_digits=16, default=0)

    def __unicode__(self):
        return "%s - %s" % (self.subportfolio.__unicode__(), self.symbol)

    def set_total(self, logged_in=False):
        if not logged_in:
            trading_login()
        self.subportfolio.set_total(logged_in=True)

    def get_total(self, logged_in=False):
        if self.agg_total_last_set < datetime.datetime.now(tz=EST5EDT()) - datetime.timedelta(minutes=5):
            if not logged_in:
                trading_login()
            self.set_total(logged_in=True)
        return self.agg_total

    def run_position_on_brokerage(self, logged_in=False):
        if self.sold or self.placed_on_brokerage or self.settled:
            return

        if not logged_in:
            trading_login()

        cash = self.subportfolio.get_allocated_cash_for_new_investments(logged_in=True)
        sportfolio_total = self.subportfolio.get_total(logged_in=True) + cash
        total = self.get_total(logged_in=True)
        goal_total = sportfolio_total * self.goal_percentage
        amount_to_buy_in_dollars = goal_total - total

        if amount_to_buy_in_dollars < 0 or amount_to_buy_in_dollars <= cash - self.subportfolio.blocked_cash:
            if amount_to_buy_in_dollars > 0:
                self.amount_blocked = amount_to_buy_in_dollars
                self.subportfolio.blocked_cash += amount_to_buy_in_dollars
                self.subportfolio.save()

            print("%s: $%s" % (self.symbol, str(amount_to_buy_in_dollars)))

            order = fractional_order(self.symbol, amount_to_buy_in_dollars)
            self.position_id = order['position']
            self.instrument_id = order['instrument']
            self.latest_order_id = order['id']
            self.placed_on_brokerage = True
            self.save()
            queue_check_position_on_brokerage.apply_async((self.pk,), countdown=2)
        else:
            queue_run_position_on_brokerage.apply_async((self.pk,), countdown=5)

    def settle(self, logged_in=False):
        if self.sold or not self.placed_on_brokerage or self.settled or not self.latest_order_id:
            return

        if not logged_in:
            trading_login()

        est_now = datetime.datetime.now(tz=EST5EDT())
        order = get_order_info(self.latest_order_id)

        if order['state'] == 'filled' and TransactionLog.objects.filter(order_id=self.latest_order_id).count() == 0:
            if order['side'] == 'buy':
                quantity = order['quantity']
            else:
                quantity = -order['quantity']
            current_quantity = self.current_quantity + Decimal(quantity)
            tl = TransactionLog(subportfolio=self.subportfolio, symbol=self.symbol, quantity=current_quantity, date=est_now, order_id=self.latest_order_id)
            tl.save()

            if order['side'] == 'buy':
                # self.subportfolio.blocked_cash -= Decimal(order['executed_notional']['amount'])
                self.subportfolio.blocked_cash -= self.amount_blocked
                self.subportfolio.save()
                self.amount_blocked = 0

            self.current_quantity = current_quantity
            self.settled_percentage = self.goal_percentage
            self.settled = True
            self.placed_on_brokerage = False
            if self.current_quantity == 0:
                self.sold = True
            self.save()

        else:
            queue_check_position_on_brokerage.apply_async((self.pk,), countdown=2)


def set_new_position(sportfolio, symbol, goal_percentage):
    try:
        p = Position.objects.get(subportfolio=sportfolio, symbol=symbol, sold=False)
        if p.goal_percentage == goal_percentage:
            return
    except:
        if goal_percentage == 0.0:
            return
        p = Position(subportfolio=sportfolio, symbol=symbol, sold=False)
    p.goal_percentage = goal_percentage
    p.settled = False
    p.placed_on_brokerage = False
    p.save()


class TransactionLog(models.Model):
    subportfolio = models.ForeignKey(SubPortfolio, on_delete=models.PROTECT)
    symbol = models.CharField(max_length=15)
    quantity = models.DecimalField(decimal_places=8, max_digits=16) #positive for buy, negative for sell
    date = models.DateTimeField()
    order_id = models.CharField(max_length=50)


