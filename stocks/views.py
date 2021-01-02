from django.shortcuts import render
from django.http import HttpResponse
import alpaca_trade_api as tradeapi #https://pypi.org/project/alpaca-trade-api/
import pandas as pd
import datetime
import pandas_datareader.data as web
import logging


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

    #return HttpResponse(str(upro))
    return HttpResponse(response)
