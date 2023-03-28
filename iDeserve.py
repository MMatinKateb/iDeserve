"""
Ichimoku Cloud Trading Bot
Author: Mohammad Matin Kateb
Email: matin.kateb.mk@gmail.com
"""

import time
import numpy as np
import matplotlib.pyplot as plt
import MetaTrader5 as mt5

# set the account information
account = 1234567
password = "password"
server = "MetaQuotes-Demo"

# login to MetaTrader 5
def login():
    """
    Logs in to a MetaTrader 5 account.
    """
    if not mt5.initialize():
        print("initialize() failed")
        quit()

    authorized = mt5.login(account, password, server)
    if not authorized:
        print("login() failed")
        mt5.shutdown()
        quit()

# logout from MetaTrader 5
def logout():
    """
    Logs out from a MetaTrader 5 account.
    """
    mt5.shutdown()

# get the account information
def get_account_info():
    """
    Gets the account information from a MetaTrader 5 account.
    """
    return mt5.account_info()

# calculate the lot size based on the equity
def calculate_lot_size(equity):
    """
    Calculates the lot size based on the equity of a MetaTrader 5 account.
    """
    lot_size = 0.1
    return min(lot_size, equity * 0.1 / 10000)

# get the historical data
def get_historical_data(symbol, timeframe, count):
    """
    Gets the historical data for a symbol from a MetaTrader 5 account.
    """
    try:
        return mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    except Exception as e:
        print("Error getting historical data for", symbol, ":", e)
        return None

# extract the OHLC data
def extract_ohlc_data(bars):
    """
    Extracts the OHLC data from a list of bars.
    """
    if bars is None:
        return None, None, None
    close = np.array([bar.close for bar in bars])
    high = np.array([bar.high for bar in bars])
    low = np.array([bar.low for bar in bars])
    return close, high, low

# calculate the Ichimoku Cloud
def calculate_ichimoku_cloud(close, high, low):
    """
    Calculates the Ichimoku Cloud for a set of OHLC data.
    """
    if close is None or high is None or low is None:
        return None, None, None, None
    tenkan_sen = (np.max(high[-9:]) + np.min(low[-9:])) / 2
    kijun_sen = (np.max(high[-26:]) + np.min(low[-26:])) / 2
    senkou_span_a = (tenkan_sen + kijun_sen) / 2
    senkou_span_b = (np.max(high[-52:]) + np.min(low[-52:])) / 2
    return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b

# place a buy order
def place_buy_order(symbol, lot_size, stop_loss_price):
    """
    Places a buy order for a symbol in a MetaTrader 5 account.
    """
    try:
        buy_price = mt5.symbol_info_tick(symbol).ask
        mt5.order_send(symbol=symbol, action=mt5.ORDER_TYPE_BUY, volume=lot_size, price=buy_price, sl=stop_loss_price)
        print("Buy order placed for", symbol, "at price:", buy_price)
    except Exception as e:
        print("Error placing buy order for", symbol, ":", e)

# place a sell order
def place_sell_order(symbol, lot_size, stop_loss_price):
    """
    Places a sell order for a symbol in a MetaTrader 5 account.
    """
    try:
        sell_price = mt5.symbol_info_tick(symbol).bid
        mt5.order_send(symbol=symbol, action=mt5.ORDER_TYPE_SELL, volume=lot_size, price=sell_price, sl=stop_loss_price)
        print("Sell order placed for", symbol, "at price:", sell_price)
    except Exception as e:
        print("Error placing sell order for", symbol, ":", e)

# set the timeframe and stop loss distance
timeframe = mt5.TIMEFRAME_H1
stop_loss = 50

def main():
    """
    The main function that runs the Ichimoku Cloud trading bot.
    """
    # login to MetaTrader 5
    login()

    while True:
        try:
            # get the account information
            account_info = get_account_info()
            equity = account_info.equity

            # calculate the lot size based on the equity
            lot_size = calculate_lot_size(equity)

            # get the symbols available
            symbols = mt5.symbols_get()

            for symbol in symbols:
                try:
                    # check if the symbol is a forex pair
                    if symbol.path.startswith("Forex"):
                        # get the historical data
                        bars = get_historical_data(symbol.name, timeframe, 100)

                        # extract the OHLC data
                        close, high, low = extract_ohlc_data(bars)

                        # calculate the Ichimoku Cloud
                        tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b = calculate_ichimoku_cloud(close, high, low)

                        # check if the price is above the cloud
                        if close is not None and high is not None and low is not None and close[-1] > senkou_span_a and close[-1] > senkou_span_b:
                            # place a buy order
                            stop_loss_price = mt5.symbol_info(symbol.name).bid - stop_loss * mt5.symbol_info(symbol.name).point
                            place_buy_order(symbol.name, lot_size, stop_loss_price)
                        # check if the price is below the cloud
                        elif close is not None and high is not None and low is not None and close[-1] < senkou_span_a and close[-1] < senkou_span_b:
                            # place a sell order
                            stop_loss_price = mt5.symbol_info(symbol.name).ask + stop_loss * mt5.symbol_info(symbol.name).point
                            place_sell_order(symbol.name, lot_size, stop_loss_price)
                except Exception as e:
                    print("Error processing symbol", symbol.name, ":", e)

            # wait for 1 hour before checking again
            time.sleep(3600)

        except KeyboardInterrupt:
            # logout from MetaTrader 5
            logout()
            break

# run the main function
if __name__ == "__main__":
    main()
