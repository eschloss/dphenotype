from django.shortcuts import render
#import alpaca_trade_api as tradeapi #https://pypi.org/project/alpaca-trade-api/
from stocks.rh_utils import *
import pandas as pd
import datetime
import pandas_datareader.data as web
from smtplib import SMTPException
from django.core.mail import EmailMultiAlternatives, get_connection
from eschadmin import settings
import logging
from stocks.eastern_time import EST5EDT
from celery import shared_task
from stocks.models import queue_run_position_on_brokerage, queue_check_position_on_brokerage, SubPortfolio, Position, set_new_position, CashAtDayStart, UserPortfolio
from django.db.models import F


SMTP_HEADERS = {'X-MC-Important': 'true'}


def cash_strategy(sportfolio):
    positions = Position.objects.filter(subportfolio=sportfolio)
    for p in positions:
        set_new_position(sportfolio, p.symbol, 0.0)


def vti_strategy(sportfolio):
    positions = Position.objects.filter(subportfolio=sportfolio)
    for p in positions:
        if p.symbol.lower() != "vti":
            set_new_position(sportfolio, p.symbol, 0.0)
    set_new_position(sportfolio, 'VTI', 1.0)


def sector_strategy_1(sportfolio):
    prev_index = -1
    comparison_index = -5
    comparison_index2 = -150
    comparison_index3 = -100
    comparison_index4 = -50
    comparison_index5 = -125
    comparison_index6 = -135

    end = datetime.datetime.now(tz=EST5EDT())
    start = end - datetime.timedelta(days=-comparison_index2 * 7 / 4)

    sector_etfs = ["VGT", "VHT", "VNQ", "VAW", "VCR", "VFH", "VDE", "VIS", "VPU", "VDC", "VOX"]
    sectors = {}
    for etf in sector_etfs:
        sectors[etf] = web.DataReader(etf, "yahoo", start, end)["Adj Close"]
    eql_close = web.DataReader("EQL", "yahoo", start, end)["Adj Close"].rename("EQL")

    trading_login()

    underperforming_sectors = []
    yesterdays_pc_change = {}
    total = 0
    for etf in sector_etfs:
        sector = sectors[etf]
        performance = sector[prev_index] / sector[comparison_index] - eql_close[prev_index] / eql_close[comparison_index]
        performance2 = sector[prev_index] / sector[comparison_index2] - eql_close[prev_index] / eql_close[comparison_index2]
        if performance < 0 < performance2:
            performance3 = sector[prev_index] / sector[comparison_index3] - eql_close[prev_index] / eql_close[comparison_index3]
            performance4 = sector[prev_index] / sector[comparison_index4] - eql_close[prev_index] / eql_close[comparison_index4]
            performance5 = sector[prev_index] / sector[comparison_index5] - eql_close[prev_index] / eql_close[comparison_index5]
            performance6 = sector[prev_index] / sector[comparison_index6] - eql_close[prev_index] / eql_close[comparison_index6]
            underperforming_sectors.append(etf)
            mod_performance = -performance / (performance2 ** 2)
            if performance4 < 0:
                mod_performance /= (-performance4)
            if performance3 < 0:
                mod_performance /= (-performance3)
            if performance5 < 0:
                mod_performance /= (-performance5)
            if performance6 < 0:
                mod_performance /= (-performance6)
            yesterdays_pc_change[etf] = mod_performance
            total += mod_performance

    sector_invest_pc = {}
    for etf in underperforming_sectors:
        sector_invest_pc[etf] = yesterdays_pc_change[etf] / total

    """ SELL OVERPERFORMING SECTORS """
    for etf in filter(lambda a: a not in underperforming_sectors, sector_etfs):
        set_new_position(sportfolio, etf, 0.0)

    """ BUY/CHANGE QUANTITY OF UNDERPERFORMING SECTORS (OR SPY) """
    if len(underperforming_sectors) > 0:
        for etf in underperforming_sectors:
            set_new_position(sportfolio, etf, sector_invest_pc[etf])
    else:
        set_new_position(sportfolio, "EQL", 100.0)


STRATEGIES = {
    '0': sector_strategy_1,
    '1': cash_strategy,
    '2': vti_strategy,
}


@shared_task
def reset_userportfolio_cash():
    for up in UserPortfolio.objects.filter(on=True):
        cash, created = CashAtDayStart.objects.get_or_create(userportfolio=up)
        cash.reset()


@shared_task
def check_positions_on_brokerage():
    positions = Position.objects.filter(subportfolio__userportfolio__on=True,
                                        sold=False, placed_on_brokerage=True, settled=False)
    for p in positions:
        queue_check_position_on_brokerage.delay(p.pk)


@shared_task
def run_positions_on_brokerage():
    positions = Position.objects.filter(subportfolio__userportfolio__on=True,
                                        sold=False, placed_on_brokerage=False, settled=False)
    sell_positions = positions.filter(goal_percentage__lt=F('settled_percentage'))
    for p in sell_positions:
        queue_run_position_on_brokerage.apply_async((p.pk,), countdown=0)

    buy_positions = positions.filter(goal_percentage__gte=F('settled_percentage'))
    for p in buy_positions:
        queue_run_position_on_brokerage.apply_async((p.pk,), countdown=5)


@shared_task
def run_subportfolios():
    est_now = datetime.datetime.now(tz=EST5EDT())
    today = est_now.replace(hour=0, minute=0, second=0, microsecond=0)

    trading_login()
    (open, close) = get_todays_hours()

    fraction_of_day = (est_now - open)/(close - open)

    sportfolios = SubPortfolio.objects.filter(userportfolio__on=True, is_being_run_currently_lock=False,
                                              run_hour__lte=fraction_of_day, agg_last_run__lt=today)
    for sp in sportfolios:
        run_subportfolio.delay(sp.pk)


@shared_task
def run_subportfolio(pk):
    sportfolio = SubPortfolio.objects.get(pk=pk)
    sportfolio.is_being_run_currently_lock = True
    sportfolio.save()

    STRATEGIES[sportfolio.strategy](sportfolio)

    est_now = datetime.datetime.now(tz=EST5EDT())
    sportfolio.agg_last_run = est_now
    sportfolio.is_being_run_currently_lock = False
    sportfolio.save()


@shared_task
def send_vix_data():
    end = datetime.datetime.now()

    vix = web.DataReader("^VIX", "yahoo", end - datetime.timedelta(hours=48), end)
    vix_high = vix["High"]
    vix_low = vix["Low"]
    vix_close = vix["Adj Close"]
    diff = vix_high[-1] - vix_low[-1]

    subject = "^VIX diff @ %s" % str(round(diff, 4))
    text_content = "if >= 9, sell stocks"
    send_mail(subject, text_content)

    logging.info("^vix task successfully run")


def send_mail(subject, text_content, from_email="stocks-eschadmin@ericschlossberg.com"):
    smtp = get_connection('django.core.mail.backends.smtp.EmailBackend', host=settings.SMTP_HOST,
                          port=settings.SMTP_PORT, username=settings.SMTP_USER, password=settings.SMTP_PASSWORD,
                          use_tls=settings.SMTP_USE_TLS)
    email_list = ['orpheuskl@gmail.com']
    msg = EmailMultiAlternatives(subject, text_content, from_email, email_list,
                                 connection=smtp, headers=SMTP_HEADERS)
    try:
        msg.send(fail_silently=False)
    except SMTPException as e:
        logging.error("Email Failed to Send smtp=%s" % (bool(smtp)))
        logging.error(e, exc_info=True)


@shared_task
def vix_near_threshold(threshold=7):
    end = datetime.datetime.now()
    vix = web.DataReader("^VIX", "yahoo", end - datetime.timedelta(hours=24), end)
    vix_high = vix["High"]
    vix_low = vix["Low"]
    diff = vix_high[-1] - vix_low[-1]
    if diff >= threshold:
        subject = "[ALERT] ^VIX diff @ %s" % str(round(diff, 4))
        text_content = "if >= 9, sell stocks"
        send_mail(subject, text_content)


@shared_task
def reset_totals():
    sps = SubPortfolio.objects.filter(userportfolio__on=True)
    trading_login()
    for sp in sps:
        sp.get_total(logged_in=True)

