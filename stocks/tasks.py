from django.shortcuts import render
import alpaca_trade_api as tradeapi #https://pypi.org/project/alpaca-trade-api/
import pandas as pd
import datetime
import pandas_datareader.data as web
from smtplib import SMTPException
from django.core.mail import EmailMultiAlternatives, get_connection
from eschadmin import settings
import logging
from celery import shared_task


SMTP_HEADERS = {'X-MC-Important': 'true'}


@shared_task
def send_vix_data():
    api = tradeapi.REST()
    end = datetime.datetime.now()
    """
    account = api.get_account()
    start = end - datetime.timedelta(hours=12)
    end_iso = end.isoformat()
    start_iso = start.isoformat()
    upro = api.get_barset(['UPRO', '^VIX'], 'day', start=start_iso, end=end_iso, limit=1)
    #upro = api.get_last_trade('UPRO')
    #api.list_positions()
    #account.status
    """

    vix = web.DataReader("^VIX", "yahoo", end - datetime.timedelta(hours=48), end)
    vix_high = vix["High"]
    vix_low = vix["Low"]
    vix_close = vix["Adj Close"]
    diff = vix_high[0] - vix_low[0]

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
    vix = web.DataReader("^VIX", "yahoo", end - datetime.timedelta(hours=12), end)
    vix_high = vix["High"]
    vix_low = vix["Low"]
    diff = vix_high[0] - vix_low[0]
    if diff >= threshold:
        subject = "[ALERT] ^VIX diff @ %s" % str(round(diff, 4))
        text_content = "if >= 9, sell stocks"
        send_mail(subject, text_content)

