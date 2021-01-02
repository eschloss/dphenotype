from django.shortcuts import render
from django.http import HttpResponse
import alpaca_trade_api as tradeapi


# Create your views here.
def home(request):
    return HttpResponse("Home Hi")

def home2(request):
    api = tradeapi.REST()
    account = api.get_account()
    api.list_positions()