import websocket,json,pprint, talib, numpy
from binance.client import Client
from binance.enums import *
import config
import datetime
from helpers import *
import time
import os
import threading
from indicators import *


class History():
    def __init__(self):
        #inits
        self.client = Client(config.API_KEY,config.API_SECRET, tld='us')
        #arrays
        self.CANDLES = []
        # self.closes = []
        self.hist_bars = []
        self.length_list = []

        #Props
        self.TRADE_SYMBOL = 'DOGEUSDT'
        self.HISTORY_INTERVAL=Client.KLINE_INTERVAL_1MINUTE
        self.TRADE_INTERVAL = "1m"
        self.SHARES = 1000


        self.barCount =  0

        self.historical_bars = 0

    # def set_closes(self,close):
    #     self.closes.append(close)
  
    def get_historical_bars(self):
        self.historical_bars = self.client.get_historical_klines(self.TRADE_SYMBOL, self.HISTORY_INTERVAL, "1 day ago UTC")
        return self.historical_bars

    def set_CANDLES(self):
        
        bars = self.get_historical_bars()

        for bar in bars:
            candle = {"date": milsToDateTime(bar[0]), "close":float(bar[4]),"open":float(bar[1]),"high":float(bar[2]),"low":float(bar[3]),"volume":float(bar[5])}
            self.CANDLES.append(candle)

    def get_CANDLES(self):
        return self.CANDLES
    
    def insert_col_n_rows(self,key,value):
        
        for row in self.CANDLES:
            row[key] = value


history = History()
indicators = Indicators()
ai = AI()
history.set_CANDLES()


#add Props
history.closes = []
history.EMA1_WINDOW = 3

#locals
CANDLES = history.get_CANDLES()
closes = history.closes

#append history.closes

# for i in range(len(CANDLES)):
#     closes.append(CANDLES[i]["close"])
    
#     EMA1 = indicators.EMA("EMA3",closes,history.EMA1_WINDOW)
#     CANDLES[i]["EMA1"] = EMA1

    

    

    #instet EMA
    # history.insert_col_n_rows("EMA1",EMA1)


# for candle in CANDLES:
#     print(candle["date"],candle["EMA1"])


