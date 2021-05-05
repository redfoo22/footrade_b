import websocket,json,pprint, talib, numpy
from binance.client import Client
from binance.enums import *
import config
import datetime
from helpers import *
import time


class Bot():

STATE = {"live":0,"long":0,"short":0,"games":0,"set_A":0,"set_B":0,"set_C":0,"simulation":0}
RSI_PERIOD =14
RSI_OVERBOUGHT =70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'DOGEUSDT'
INTERVAL = "1m"
TRADE_QUANTITY = 5000
SELL_QUANTITY = 5000
in_position = False
CANDLES = []
closes =[]
barCount =  0
last_rsi = 0
tick_price = 0
avg_trade_entry_price =0
avg_trade_exit_price =0
trade_entry_prices = []
trade_ticks = []
trade_tick_high = 0
trail_stop_price = 0
STOP_LOSS = 0.03
TAKE_PROFIT = .003
diff_value = .003
TRAIL_STOP_VALUE = .003
EMA1_WINDOW = 8
EMA2_WINDOW = 20
purchased_shares  = 0
tickCounter = 0
napper = 0
vers = 'shorting'
i=0
running_profit = 0
shares =10000
EMA_to_low_diff_short =0
EMA_to_low_diff = 0
STRAT_DIFF = 0
    def __init__(self):
    
        
        self.SOCKET = f'wss://stream.binance.com:9443/ws/{self.TRADE_SYMBOL}@kline_{self.INTERVAL}'
        
        #GLOBALS
        
        
       
        

    def update(self, data):
       pass 
    
    
       

















if __name__ == "__main__":