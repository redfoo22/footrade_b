import websocket,json,pprint, talib, numpy

from binance.client import Client
from binance.enums import *
import config
import datetime
from helpers import *
import time
import os
import threading

client = Client(config.API_KEY,config.API_SECRET, tld='us')

class Hedge_Short():
    def __init__(self):
        self.vers = "hedge"
        self.TRADE_SYMBOL = "DOGEUSDT"
        
        self.trade_entry_prices = []
        self.trade_exit_prices = []
        self.entry_price = 0
        self.exit_price = 0
        self.running_profit = 0
        self.rebalancing = 0
        self.MIN_SHARES = 700
        self.SHARES = self.MIN_SHARES
        self.tp = 0.01
        #git
        
        self.TRADES_dict= {"ID":1,"entry_date":datetime.datetime.now(),"exit_date":None,"entry_price":0,"exit_price":0,"shares":0,"symbol":"DOGEUSDT","tp":0,"long":0,"open":0,"closed":0,"profit":0}

        # self.trades = []

        self.trades_updated = []
    
    def print_shit(self,close):
        pass
        

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

    def read_list_from_file(self,name):
        name =name

        
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



    def hedge_strat_short(self,close,EMA_item):
        #SELL
        self.short_close_condition(close)
        # print("sleeping")
        # time.sleep(2)
        # print("awake")
        #short
        print("running short condish")
        self.short_condition(close,EMA_item)
        

    def read_financials_from_file(self,name):
        name =name

       
        if self.is_file_empty_3(name) == False:

            FILE = open(name, 'r')
            temp_array = []
            
            for line in FILE:
                # remove linebreak which is the last character of the string
                item = line[:-1]

                #add item to the list
                temp_array.append(item)
            
            temp_array = [eval(item) for item in temp_array]
            financials_from_file = temp_array[-1]
            temp_array = []

            
            FILE.close()
            return financials_from_file

    def get_shares_to_short(self):
        row = self.read_financials_from_file("financials.txt")
        return row["shorts_to_buy"]


        
    def add_ID(self):
        IDs = []
        if len(self.trades_updated) >0:
            for trade in self.trades_updated:
                IDs.append(int(trade["ID"]))
            maxID = max(IDs)
            return maxID +1
        else:
            return 1

    


            
    def short_condition(self,close,EMA_item):
        
        
        if close <= EMA_item:
           self.SHORT()

           

    def short_close_condition(self,close):
        
        self.read_list_from_file("hedge_TRADES.txt") #???
        closed_IDs = []
        only_1_IDs = []
        idss = []
        if len(self.trades_updated) >0:
            for i in range(len(self.trades_updated)):
                idss.append(self.trades_updated[i]["ID"])
            for y in range(len(idss)):
                if idss.count(self.trades_updated[y]["ID"]) ==1:
                     only_1_IDs.append(self.trades_updated[y])
            for trade in only_1_IDs: #loop in reverse
                if close <= trade["entry_price"] - trade["entry_price"] * self.tp or close >= trade["entry_price"] + trade["entry_price"] * self.tp:
                    self.SHORT_CLOSE(trade)


    def tp_price(self,entry_price):
        tp_price_ = entry_price + entry_price *.01
        return tp_price_

    def SHORT_CLOSE(self,trade):
        
            
        for i in range(len(self.trades_updated)-1,-1,-1):
            if trade["ID"] == self.trades_updated[i]["ID"] and self.trades_updated[i]["closed"] ==1:
                return

            else:
                if trade["ID"] == self.trades_updated[i]["ID"] and self.trades_updated[i]["open"] ==1 and self.trades_updated[i]["short"] ==1:
                    
                    order = client.order_market_buy(
                    symbol=trade["symbol"],
                    quantity=trade["shares"])
                    print(order)
                    self.rebalancing = 1

                    


                    for obj in order["fills"]:
                        
                        self.trade_exit_prices.append(float(obj["price"]))
                        # print(f'last trade entry price {trade_entry_prices[-1]}')
                    # if len(trade_entry_prices) > 1:
                    #     avg_trade_exit_price = sum(trade_entry_prices) / len(trade_entry_prices)
                    # else:
                    self.exit_price = self.trade_exit_prices[-1]

                    profit = trade["entry_price"] - self.exit_price 
                
                    self.running_profit += profit

                #states
                    self.trades_updated[i]["open"] = 0
                    
                    self.trades_updated[i]["closed"] = 1


                    self.trades_updated[i]["exit_price"] = self.exit_price
                    self.trades_updated[i]["exit_date"] = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                    self.trades_updated[i]["profit"] = profit

                    row_in_mem = self.trades_updated[i]
                    self.write_list_to_file("hedge_TRADES.txt",row_in_mem)

                    print(f'SHORT_CLOSEDDDD ID: {self.trades_updated[i]["ID"]} exit date: {self.trades_updated[i]["exit_date"]} exit_price: {self.trades_updated[i]["exit_price"]} entry_price: {self.trades_updated[i]["entry_price"]} profit {self.trades_updated[i]["profit"]} Running Profit: {self.running_profit}')


    def SHORT(self):
        try:
            print("SHORT CALLED and rebalancing is",self.rebalancing)
        # if STATE["simulation"]==1:
        
        #     avg_trade_entry_price = hist_bars[-1]["close"]

        #     print(f'{hist_bars[-1]["date"]} BUYYYYYYYYY Entrty Price: {avg_trade_entry_price}')

        #state
        

            #self.TRADES_dict= {"ID":1,"entry_date":datetime.datetime.now(),"exit_date":None,"entry_price":0,"exit_price":0,"shares":0,"symbol":"DOGE","tp":0,"long":0,"open":0,"closed":0,"running_profit":0}
            #self.trades = []
            if self.rebalancing ==1:
                self.SHARES = self.get_shares_to_short()
                order = client.order_market_sell(
                symbol=self.TRADE_SYMBOL,
                quantity=self.SHARES)
                print(order)
                self.rebalancing = 0
            else:
                self.SHARES = self.MIN_SHARES
                order = client.order_market_sell(
                symbol=self.TRADE_SYMBOL,
                quantity=self.SHARES)
                print(order)


                    

            

            for obj in order["fills"]:
            
                self.trade_entry_prices.append(float(obj["price"]))
        
            self.entry_price = self.trade_entry_prices[-1]

        

            #make Row
            row = {"ID":self.add_ID(),"entry_date":datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),"exit_date":None,"entry_price":self.entry_price,"exit_price":0,"shares":self.SHARES,"symbol":self.TRADE_SYMBOL,"tp_price": self.tp_price(self.entry_price),"long":0,"short":1,"open":1,"closed":0,"profit":0}

            #write trade to file
            self.write_list_to_file("hedge_TRADES.txt",row)

            #empty trades arry
        

            self.read_list_from_file("hedge_TRADES.txt")

            print(f'SHORTTTTTT ID: {self.trades_updated[-1]["ID"]} date: {self.trades_updated[-1]["entry_date"]} Entry_price: {self.trades_updated[-1]["entry_price"]} TP: {self.trades_updated[-1]["tp_price"]}')
            
        except Exception as e:
            print("THERE IS AN ERROR",e)    
        
        # email_Text(f'BUYYYYYYY ID: {self.trades_updated[-1]["ID"]}  Entry_price: {self.trades_updated[-1]["entry_price"]} TP: {self.trades_updated[-1]["tp_price"]}',self.vers)    