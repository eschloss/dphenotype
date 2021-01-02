from django.shortcuts import render
from django.http import HttpResponse
import alpaca_trade_api as tradeapi #https://pypi.org/project/alpaca-trade-api/
import pandas as pd
import datetime
import pandas_datareader.data as web
from smtplib import SMTPException
from django.core.mail import EmailMultiAlternatives, get_connection
from eschadmin import settings
import logging

# Create your views here
def home(request):
    response = ""
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
    response += "^VIX High: %s<br/>" % str(vix_high[0])
    response += "^VIX Low: %s<br/>" % str(vix_low[0])
    response += "^VIX Close: %s<br/>" % str(vix_close[0])
    response += "^VIX Diff: %s<br/>" % str(vix_high[0] - vix_low[0])
    response += "If ^VIX Diff is >= 9, sell<br/>"

    smtp = get_connection('django.core.mail.backends.smtp.EmailBackend', host=settings.SMTP_HOST,
                          port=settings.SMTP_PORT, username=settings.SMTP_USER, password=settings.SMTP_PASSWORD,
                          use_tls=settings.SMTP_USE_TLS)
    subject = "Daily ^VIX"
    text_content = "nothing yet"
    from_email = "info@eschadmin.heroku.com"
    email_list = ['orpheuskl@gmail.com']
    msg = EmailMultiAlternatives(unicode(subject), text_content, from_email, [from_email], bcc=email_list,
                                 connection=smtp, headers=SMTP_HEADERS)
    try:
        msg.send(fail_silently=False)
    except SMTPException as e:
        logging.error("Email Failed to Send smtp=%s bcc=%s" % (bool(smtp), bcc))
        logging.error(e, exc_info=True)

    #return HttpResponse(str(upro))
    return HttpResponse(response)
