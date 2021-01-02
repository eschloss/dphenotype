from django.shortcuts import render
from django.http import HttpResponse
import alpaca_trade_api as tradeapi


# Create your views here.
def home(request):
    api = tradeapi.REST()
    account = api.get_account()
    return HttpResponse(api.list_positions())
