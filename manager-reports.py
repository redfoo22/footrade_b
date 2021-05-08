import websocket,json,pprint, talib, numpy

from binance.client import Client
from binance.enums import *
import config
import datetime
from helpers import *
import time
import os


class Manager():
    def __init__(self):
        #setups
        self.vers = "hedge"
        self.TRADE_SYMBOL = "DOGEUSDT"
        self.long_shares = 0
        self.HISTORY_INTERVAL=Client.KLINE_INTERVAL_1MINUTE
        self.TRADE_INTERVAL = "1m"
        self.MIN_SHARES = 1000

        self.foo_email = "3102796480@tmomail.net"
        self.alex_email = "3235594184@vtext.com"

        self.SOCKET = f'wss://stream.binance.com:9443/ws/{self.TRADE_SYMBOL.lower()}@kline_{self.TRADE_INTERVAL}'

        # self.client = Client(config.API_KEY,config.API_SECRET, tld='us')

        self.running_profit = 0
        self.trades_updated = []


        self.financials = {}

        #bars
        self.close = 0

        #RT
        self.tick_price = 0

    def update(self,close_):
        self.set_close(close_)

        #GET and PRINT BALANCES
        self.get_current_balance(self.get_close())



        self.set_financials(self.get_close())
        self.write_finanicials_to_file("financials.txt",self.create_shares_to_open_row())



        

        







    def set_close(self,close):
        self.close = close
    def get_close(self):
        return self.close 

    def set_financials(self,close):
        self.financials = {"short_shares":self.get_open_short_shares(),"long_shares":self.get_open_long_shares(),"diff":self.get_diff(self.get_open_long_shares(),self.get_open_short_shares())}

    def get_diff(self,a,b):
        diff = a-b #longs-shorts
        return diff
    
    def get_financials(self):
        return self.financials

    def get_longs_to_buy(self):
        financials = self.get_financials()
        diff = financials["diff"]
        short_shares = financials["short_shares"]
        long_shares = financials["long_shares"]
        longs_to_buy = 0
        if diff < 0:
            longs_to_buy = abs(diff)
            return longs_to_buy
        else:
            return self.MIN_SHARES
    
    def get_shorts_to_buy(self):
        financials = self.get_financials()
        diff = financials["diff"]
        short_shares = financials["short_shares"]
        long_shares = financials["long_shares"]
        shorts_to_buy = 0
        if diff > 0:
            shorts_to_buy = abs(diff)
            return shorts_to_buy
        else:
            return self.MIN_SHARES
    

        #fintec logic
    def get_short_losses(self,close):
        self.read_list_from_file("hedge_TRADES.txt") #???
        closed_IDs = []
        only_1_IDs = []
        idss = []
        loss = 0
        losses = []
        if len(self.trades_updated) >0:
            for i in range(len(self.trades_updated)):
                idss.append(self.trades_updated[i]["ID"])
            for y in range(len(idss)):
                if idss.count(self.trades_updated[y]["ID"]) ==1:
                     only_1_IDs.append(self.trades_updated[y])
            for trade in only_1_IDs: #loop in reverse
                if trade["short"] ==1 and trade["open"] ==1:
                    loss = trade["entry_price"] - close
                    losses.append(loss)
        return sum(losses)
    
    def get_long_losses(self,close):
        self.read_list_from_file("hedge_TRADES.txt") #???
        closed_IDs = []
        only_1_IDs = []
        idss = []
        loss = 0
        losses = []
        if len(self.trades_updated) >0:
            for i in range(len(self.trades_updated)):
                idss.append(self.trades_updated[i]["ID"])
            for y in range(len(idss)):
                if idss.count(self.trades_updated[y]["ID"]) ==1:
                     only_1_IDs.append(self.trades_updated[y])
            for trade in only_1_IDs: #loop in reverse
                if trade["long"] ==1 and trade["open"] ==1:
                    loss = trade["entry_price"] - close
                    losses.append(loss)
        return sum(losses)
    
    def get_long_wins(self,close):
        self.read_list_from_file("hedge_TRADES.txt") #???
        closed_IDs = []
        only_1_IDs = []
        idss = []
        win = 0
        wins = []
        if len(self.trades_updated) >0:
            for i in range(len(self.trades_updated)):
                if self.trades_updated[i]["long"]==1 and self.trades_updated[i]["closed"] == 1:
                    wins.append(self.trades_updated[i]["profit"])
        return sum(wins)
    
    def get_short_wins(self,close):
        self.read_list_from_file("hedge_TRADES.txt") #???
        closed_IDs = []
        only_1_IDs = []
        idss = []
        win = 0
        wins = []
        if len(self.trades_updated) >0:
            for i in range(len(self.trades_updated)):
                if self.trades_updated[i]["short"]==1 and self.trades_updated[i]["closed"] == 1:
                    wins.append(self.trades_updated[i]["profit"])
        return sum(wins)

    def get_current_balance(self,close):
        total_wins = self.get_long_wins(close) + self.get_short_wins(close)
        print(f'TOTAL_WINS:{total_wins}')
        total_losses = self.get_short_losses(close)
        print(f'TOTAL LOSS: {total_losses}')

        balance = total_wins + total_losses
        print(f'BALANCE   : {balance}')
        return balance
    
    
    def get_open_short_shares(self):
        self.read_list_from_file("hedge_TRADES.txt") #???
        closed_IDs = []
        only_1_IDs = []
        idss = []
        shares = 0
        total_shares = []
        if len(self.trades_updated) >0:
            for i in range(len(self.trades_updated)):
                idss.append(self.trades_updated[i]["ID"])
            for y in range(len(idss)):
                if idss.count(self.trades_updated[y]["ID"]) ==1:
                     only_1_IDs.append(self.trades_updated[y])
            for trade in only_1_IDs: #loop in reverse
                if trade["short"] ==1 and trade["open"] ==1:
                    shares = trade["shares"]
                    total_shares.append(shares)
        return sum(total_shares)

    def get_open_long_shares(self):
        self.read_list_from_file("hedge_TRADES.txt") #???
        closed_IDs = []
        only_1_IDs = []
        idss = []
        shares = 0
        total_shares = []
        if len(self.trades_updated) >0:
            for i in range(len(self.trades_updated)):
                idss.append(self.trades_updated[i]["ID"])
            for y in range(len(idss)):
                if idss.count(self.trades_updated[y]["ID"]) ==1:
                     only_1_IDs.append(self.trades_updated[y])
            for trade in only_1_IDs: #loop in reverse
                if trade["long"] ==1 and trade["open"] ==1:
                    shares = trade["shares"]
                    total_shares.append(shares)
                    print(f'ID: {trade["ID"]} tp: {trade["tp_price"]}')
        return sum(total_shares)

    def create_shares_to_open_row(self):
        shares_to_open = {"date":datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"), "longs_to_buy":self.get_longs_to_buy(),"shorts_to_buy":self.get_shorts_to_buy()}
        return shares_to_open

                    

            
                

    
    def print_shit(self,close=0):
        pass
        # print("were live")
        

    def is_file_empty_3(self,file_name):
    #""" Check if file is empty by reading first character in it"""
    # open ile in read mode
        with open(file_name, 'r') as read_obj:
            # read first character
            one_char = read_obj.read(1)
            # if not fetched then file is empty
            if not one_char:
                return True
            else:
                return False


    def write_list_to_file(self,name,trade_execution):
        # places = ['Berlin', 'Cape Town', 'Sydney', 'Moscow']

        FILE = open(f'{name}',"a")
        
        FILE.writelines('%s\n' % trade_execution)
        FILE.close()

    def write_finanicials_to_file(self,name,data):
        # places = ['Berlin', 'Cape Town', 'Sydney', 'Moscow']

        FILE = open(f'{name}',"a")
        
        FILE.writelines('%s\n' % data)
        FILE.close()

    def read_list_from_file(self,name):
        name =name

        print("read called")
        if self.is_file_empty_3(name) == False:

            FILE = open(name, 'r')
            temp_array = []
            
            for line in FILE:
                # remove linebreak which is the last character of the string
                item = line[:-1]

                #add item to the list
                temp_array.append(item)
            
            temp_array = [eval(item) for item in temp_array]
            self.trades_updated = temp_array
            temp_array = []

            
            FILE.close()
            return self.trades_updated


#inits
manager = Manager()

#static
# manager.read_list_from_file("hedge_TRADES.txt"


def on_open(ws):
    print(' open sesame')
    

def on_close(ws):
    print('closed connection')




def on_message(ws,message):
    
    try:    

        json_message = json.loads(message)
        
        candle = json_message['k']
        
        is_candle_closed = candle['x']
        
        close = float(candle['c'])

        tick_price = float(candle['c'])

        # manager.print_shit()

        ##RT


        ###BAR CLOSSES
        if is_candle_closed:
            time.sleep(2)
            manager.update(close)
            # print("open long shares",manager.get_open_long_shares())
            # print("open short shares",manager.get_open_short_shares())




        

    except Exception as e:
        print("THERE IS AN ERROR",e)

ws = websocket.WebSocketApp(manager.SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)

ws.run_forever()
