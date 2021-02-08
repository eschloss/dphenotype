import robin_stocks as rs
import pyotp
from eschadmin.settings import RH_USERNAME, RH_PASSWORD, RH_2Factor
from decimal import Decimal


def trading_login():
    totp = pyotp.TOTP(RH_2Factor).now()
    rs.login(username=RH_USERNAME,
             password=RH_PASSWORD,
             by_sms=True, mfa_code=totp)


def get_positions():
    return rs.account.get_all_positions()


def get_stock_value_by_url(url):
    i = rs.stocks.get_instrument_by_url(url)
    symbol = i['symbol']
    return get_stock_value_by_symbol(symbol)


def get_stock_value_by_symbol(symbol):
    val = rs.stocks.get_latest_price(symbol)[0]
    return Decimal(val)


def get_stock_values_by_symbol_list(symbol_list):
    val_list = rs.stocks.get_latest_price(symbol_list)
    return list(map(lambda a: Decimal(a), val_list))


def get_available_cash():
    profile = rs.profiles.load_account_profile()
    return Decimal(profile['cash'])  # or should I be using 'portfolio_cash'


def fractional_order(symbol, amount, extended_hours=True):
    if amount >= 1.00:
        order = rs.orders.order_buy_fractional_by_price(symbol, amount, extendedHours=extended_hours)
    elif amount <= 1.00:
        order = rs.orders.order_sell_fractional_by_price(symbol, -amount, extendedHours=extended_hours)

    return order


def get_order_info(order_id):
    order = rs.orders.get_stock_order_info(order_id)
    return order
