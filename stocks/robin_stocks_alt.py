from uuid import uuid4

import robin_stocks.helper as helper
import robin_stocks.profiles as profiles
import robin_stocks.stocks as stocks
import robin_stocks.urls as urls

@helper.login_required
def order_sell_fractional_by_price(symbol, amountInDollars, timeInForce='gfd', extendedHours=False, jsonify=True):
    """Submits a market order to be executed immediately for fractional shares by specifying the amount in dollars that you want to trade.
    Good for share fractions up to 6 decimal places. Robinhood does not currently support placing limit, stop, or stop loss orders
    for fractional trades.
    :param symbol: The stock ticker of the stock to purchase.
    :type symbol: str
    :param amountInDollars: The amount in dollars of the fractional shares you want to buy.
    :type amountInDollars: float
    :param timeInForce: Changes how long the order will be in effect for. 'gfd' = good for the day.
    :type timeInForce: Optional[str]
    :param extendedHours: Premium users only. Allows trading during extended hours. Should be true or false.
    :type extendedHours: Optional[str]
    :param jsonify: If set to False, function will return the request object which contains status code and headers.
    :type jsonify: Optional[str]
    :returns: Dictionary that contains information regarding the purchase of stocks, \
    such as the order id, the state of order (queued, confired, filled, failed, canceled, etc.), \
    the price, and the quantity.
    """
    if amountInDollars < 1:
        print("ERROR: Fractional share price should meet minimum 1.00.", file=helper.get_output())
        return None
    # turn the money amount into decimal number of shares
    price = next(iter(stocks.get_latest_price(symbol, 'bid_price', extendedHours)), 0.00)
    fractional_shares = 0 if (price == 0.00) else helper.round_price(amountInDollars/float(price))

    return order(symbol, fractional_shares, amountInDollars, "sell", None, None, timeInForce, extendedHours, jsonify)

@helper.login_required
def order_buy_fractional_by_price(symbol, amountInDollars, timeInForce='gfd', extendedHours=False, jsonify=True):
    """Submits a market order to be executed immediately for fractional shares by specifying the amount in dollars that you want to trade.
    Good for share fractions up to 6 decimal places. Robinhood does not currently support placing limit, stop, or stop loss orders
    for fractional trades.
    :param symbol: The stock ticker of the stock to purchase.
    :type symbol: str
    :param amountInDollars: The amount in dollars of the fractional shares you want to buy.
    :type amountInDollars: float
    :param timeInForce: Changes how long the order will be in effect for. 'gfd' = good for the day.
    :type timeInForce: Optional[str]
    :param extendedHours: Premium users only. Allows trading during extended hours. Should be true or false.
    :type extendedHours: Optional[str]
    :param jsonify: If set to False, function will return the request object which contains status code and headers.
    :type jsonify: Optional[str]
    :returns: Dictionary that contains information regarding the purchase of stocks, \
    such as the order id, the state of order (queued, confired, filled, failed, canceled, etc.), \
    the price, and the quantity.
    """
    if amountInDollars < 1:
        print("ERROR: Fractional share price should meet minimum 1.00.", file=helper.get_output())
        return None

    # turn the money amount into decimal number of shares
    price = next(iter(stocks.get_latest_price(symbol, 'ask_price', extendedHours)), 0.00)
    fractional_shares = 0 if (price == 0.00) else helper.round_price(amountInDollars/float(price))

    return order(symbol, fractional_shares, amountInDollars, "buy", None, None, timeInForce, extendedHours, jsonify)


@helper.login_required
def order(symbol, quantity, amountInDollars, side, limitPrice=None, stopPrice=None, timeInForce='gtc', extendedHours=False, jsonify=True):
    """A generic order function.
    :param symbol: The stock ticker of the stock to sell.
    :type symbol: str
    :param quantity: The number of stocks to sell.
    :type quantity: int
    :param side: Either 'buy' or 'sell'
    :type side: str
    :param limitPrice: The price to trigger the market order.
    :type limitPrice: float
    :param stopPrice: The price to trigger the limit or market order.
    :type stopPrice: float
    :param timeInForce: Changes how long the order will be in effect for. 'gtc' = good until cancelled. \
    'gfd' = good for the day.
    :type timeInForce: str
    :param extendedHours: Premium users only. Allows trading during extended hours. Should be true or false.
    :type extendedHours: Optional[str]
    :param jsonify: If set to False, function will return the request object which contains status code and headers.
    :type jsonify: Optional[str]
    :returns: Dictionary that contains information regarding the purchase or selling of stocks, \
    such as the order id, the state of order (queued, confired, filled, failed, canceled, etc.), \
    the price, and the quantity.
    """
    try:
        symbol = symbol.upper().strip()
    except AttributeError as message:
        print(message, file=helper.get_output())
        return None

    orderType = "market"
    trigger = "immediate"

    if side == "buy":
        priceType = "ask_price"
    else:
        priceType = "bid_price"

    if limitPrice and stopPrice:
        price = helper.round_price(limitPrice)
        stopPrice = helper.round_price(stopPrice)
        orderType = "limit"
        trigger = "stop"
    elif limitPrice:
        price = helper.round_price(limitPrice)
        orderType = "limit"
    elif stopPrice:
        stopPrice = helper.round_price(stopPrice)
        if side == "buy":
            price = stopPrice
        else:
            price = None
        trigger = "stop"
    else:
        price = helper.round_price(next(iter(stocks.get_latest_price(symbol, priceType, extendedHours)), 0.00))

    payload = {
        'account': profiles.load_account_profile(info='url'),
        'instrument': stocks.get_instruments_by_symbols(symbol, info='url')[0],
        'symbol': symbol,
        'price': price,
        'quantity': quantity,
        'dollar_based_amount': {'amount': "%.2f" % amountInDollars, 'currency_code': "USD"},
        'ref_id': str(uuid4()),
        'type': orderType,
        'stop_price': stopPrice,
        'time_in_force': timeInForce,
        'trigger': trigger,
        'side': side,
        'extended_hours': extendedHours,
    }

    url = urls.orders()
    data = helper.request_post(url, payload, jsonify_data=jsonify)

    return(data)