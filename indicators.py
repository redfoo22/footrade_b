import websocket,json,pprint, talib, numpy
from binance.client import Client
from binance.enums import *
import config
import datetime
from helpers import *
import time
import os
import threading

class Indicators():
    def __init__(self):
        pass




    def EMA(self,name,list,window):
        if len(list) > window:
            np_closes1 = numpy.array(list)
            ema = talib.EMA(np_closes1, window)
            # print(f'{name} first value is {ema[-1]}')
            return ema[-1]
        else:
            return 0
class ARR():
    def __init__(self):
        self.arr = []

class AI():
    def __init__(self):
        
        #arrays
        self.max_highs = []
        self.max_lows = []
        self.min_tick_lows = []
        self.max_tick_highs = []
        
        self.closes = []
        self.diff_of_abs =[]

        print("Init success")


        # self.SOCKET = f'wss://stream.binance.com:9443/ws/{self.TRADE_SYMBOL}@kline_{self.INTERVAL}'
        
        #GLOBALS
    def EMA(self,name,list,window):
        if len(list) > window:
            np_closes1 = numpy.array(list)
            ema = talib.EMA(np_closes1, window)
            # print(f'{name} first value is {ema[-1]}')
            return ema[-1]
        else:
            return 0
        
       
    def get_highs_EMA(self,window):
        highs_EMA_ = self.EMA("highs_EMA",self.max_highs,window)
        return highs_EMA_
        
    
    def get_lows_EMA(self,window):
        lows_EMA_ = self.EMA("lows_EMA",self.max_lows,window)
        return lows_EMA_
    
    def get_tick_EMA(self,tick,window):
        

        self.closes.append(tick)
        tick_EMA_ = self.EMA("tick_closes_EMA",self.closes,window)
        self.closes.pop(-1)
        return tick_EMA_

        

    def set_highs(self,high):
        self.max_highs.append(high)

    def set_lows(self,low):
        self.max_lows.append(low)
    
    def set_closes(self,close):
        self.closes.append(close)


    def diff_of_ab(self,a,b):
        diff = a-b
        return diff
    def set_diff_of_abs(self,value):
        self.diff_of_abs.append(value)

    def get_diff_of_abs(self):
        return self.diff_of_abs
    


        



    


    def tick_lows_EMA(self,tick,window):
        self.min_tick_lows.append(tick)

        self.max_lows.append(min(self.min_tick_lows))
        tick_EMA_ = self.EMA("tick_EMA",self.max_lows,window)
        self.max_lows.pop(-1)
        return tick_EMA_
    def tick_highs_EMA(self,tick,window):
        self.max_tick_highs.append(tick)

        self.max_highs.append(max(self.max_tick_highs))
        tick_EMA_ = self.EMA("tick_EMA",self.max_highs,window)
        self.max_highs.pop(-1)
        return tick_EMA_