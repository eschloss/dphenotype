from django.shortcuts import render
from django.http import HttpResponse
from stocks.rh_utils import trading_login, get_positions
import pandas as pd
import datetime
import pandas_datareader.data as web
import logging


def home(request):
    response = ""
    end = datetime.datetime.now()

    vix = web.DataReader("^VIX", "yahoo", end - datetime.timedelta(hours=48), end)
    vix_high = vix["High"]
    vix_low = vix["Low"]
    vix_close = vix["Adj Close"]
    response += "^VIX High: %s<br/>" % str(vix_high[-1])
    response += "^VIX Low: %s<br/>" % str(vix_low[-1])
    response += "^VIX Close: %s<br/>" % str(vix_close[-1])
    response += "^VIX Diff: %s<br/>" % str(vix_high[-1] - vix_low[-1])
    response += "<br/>If ^VIX Diff is >= 9, sell<br/>"

    if vix_high[-1] - vix_low[-1] >= 9:
        status_near = 'ALERT - Sell Stocks'
    elif vix_high[-1] - vix_low[-1] > 6:
        status_near = 'Warning'
    else:
        status_near = 'Low'

    response += "<br/><br/>%s<br/>" % status_near

    trading_login()
    positions = get_positions()

    response += "<br/>%s" % str(positions[0:3])

    return HttpResponse(response)
