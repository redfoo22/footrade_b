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

class Long_():
    def __init__(self):
        self.vers = "latest"
        self.TRADE_SYMBOL = "DOGEUSDT"
        
        self.trade_entry_prices = []
        self.trade_exit_prices = []
        self.entry_price = 0
        self.exit_price = 0
        self.running_profit = 0
        self.rebalancing = 0
        self.MIN_SHARES = 100
        self.SHARES = self.MIN_SHARES
        self.tp = .01
        self.tick_price = 0
        self.EMA3_tick =0
        self.can_buy = 1
        #git
        
        self.TRADES_dict= {"ID":1,"entry_date":datetime.datetime.now(),"exit_date":None,"entry_price":0,"exit_price":0,"shares":0,"symbol":"DOGEUSDT","tp":0,"long":0,"open":0,"closed":0,"profit":0}

        # self.trades = []

        self.trades_updated = []


    def set_can_buy(self,value):
        self.can_buy=value


    def set_tp(self,value):
        self.tp=value
    def set_tick(self,value):
        self.tick_price = value
    
    def email_Text(self,sub,msg):
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        

        email = "redfoo@partyrock.com" # the email where you sent the email
        password = config.GMP
        send_to_email = "redfoo@partyrock.com" # for whom
        subject = sub
        message = msg

        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = send_to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, password)
        text = msg.as_string()
        server.sendmail(email, send_to_email, text)
        server.quit()
    

    
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



    def hedge_strat(self,close,EMA_item):
        #SELL
        # self.sell_condition(close)
        # print("hedge long sleeping","close",close)
        # time.sleep(2)
        # print("woke")
        #BUY
        print("running buy condish")
        self.buy_condition(close,EMA_item)
        

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

    def get_shares_to_long(self):
        row = self.read_financials_from_file("financials.txt")
        return row["longs_to_buy"]


        
    def add_ID(self):
        IDs = []
        if len(self.trades_updated) >0:
            for trade in self.trades_updated:
                IDs.append(int(trade["ID"]))
            maxID = max(IDs)
            return maxID +1
        else:
            return 1

    def buy_when_tick_low(self,tick,window):
        tick_low = self.ai.tick_lows_EMA(self,tick,window)

        if tick < tick_low:
            if self.can_buy ==1:
                print('buuying tikLow')
                # self.BUY_MARKET()
    

    def buy_tick_is_one_percent_lower(self,tick,list):
        lows= []
        for i in range(len(list[-60:])):
           
                
            length = 60
            
           
    
            diff=list[i-length]["EMA1"]-list[i-length-1]["low"]


            

            if diff > list[i-length-1]["close"] *.003:
                pass
                # print(list[i-length-1]["date"],diff)

            
            if diff > list[i-length-1]["close"] *.003 :
                
                
                lows.append(round(diff,5))
        max_lows = max(lows)
        
       
        avg_lows = sum(lows)/len(lows)
        # avg_lows = avg_lows *1.5
        # print(" avg lows",avg_lows)
        # print(" max lows",max_lows)

        one_percent_lower = list[-1]["EMA1"] - tick >= avg_lows *1.50

        # print(list[-1]["EMA1"]-tick,"vs", avg_lows *1.50)

        # print(one_percent_lower)

        if one_percent_lower == True:
        
            if self.can_buy ==1:
                # print("buyying one percent lower")
                
                self.BUY_MARKET()


        
        

    def buy_condition_tick(self,tick,tick_EMA_item,list,list2):
        
        if len(list2) ==0:
            if tick > tick_EMA_item:
                if list[-2] < tick_EMA_item:
                    print("crossed above ema 3 baby")
                    if self.can_buy ==1:
                        self.BUY_MARKET()
        if len(list2) >0:
            if tick > tick_EMA_item:
                if tick > list2[-1]["high"]:
                    print("crossed above ema 3 slanting up and > prev high ")
                    if self.can_buy ==1:
                        self.BUY_MARKET()
                    # if list[-2] < tick_EMA_item:
                    #     if list2[-2]["EMA1"]< tick_EMA_item:
                            
        
            


            
    def buy_condition(self,close,EMA_item):
        pass
       
        
        # if close > EMA_item or close < EMA_item:
        #     self.BUY_MARKET()

        

    def sell_condition(self,close):
        
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
                        # if close >= trade["entry_price"] + trade["entry_price"] * self.tp or close <= trade["entry_price"] - trade["entry_price"] * self.tp :
                        #     self.SELL_MARKET(trade)
                if close <= trade["entry_price"] - trade["entry_price"] * self.tp :
                            self.SELL_MARKET(trade)

                        
    def sell_condition_tick(self,tick):
        self.tick_price = tick
        
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
                        

                        if self.tick_price >= trade["entry_price"] + trade["entry_price"] * self.tp:
                            print("taking profit on the tick")
                            self.SELL_MARKET(trade)
                        


    def tp_price(self,entry_price):
        tp_price_ = entry_price + entry_price *self.tp
        return tp_price_

    def SELL_MARKET(self,trade):
        print("SELL CALLED")
        
            
        for i in range(len(self.trades_updated)-1,-1,-1):
            if trade["ID"] == self.trades_updated[i]["ID"] and self.trades_updated[i]["closed"] ==1:
                print("BUY ALREADY CLOSED")
                return

            else:
                if trade["ID"] == self.trades_updated[i]["ID"] and self.trades_updated[i]["open"] ==1 and self.trades_updated[i]["long"] ==1:
                    order = client.order_market_sell(
                    symbol=trade["symbol"],
                    quantity=trade["shares"])
                    print(order)


                    for obj in order["fills"]:
                        
                        self.trade_exit_prices.append(float(obj["price"]))
                    
                    self.exit_price = self.trade_exit_prices[-1]

                    profit = self.exit_price - trade["entry_price"]
                
                    self.running_profit += profit

                #states
                    self.trades_updated[i]["open"] = 0
                    
                    self.trades_updated[i]["closed"] = 1


                    self.trades_updated[i]["exit_price"] = self.exit_price
                    self.trades_updated[i]["exit_date"] = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                    self.trades_updated[i]["profit"] = profit

                    row_in_mem = self.trades_updated[i]
                    self.write_list_to_file("hedge_TRADES.txt",row_in_mem)

                    


                    # self.rebalancing = 1

                    print(f'SELLlll ID: {self.trades_updated[i]["ID"]} exit date: {self.trades_updated[i]["exit_date"]} exit_price: {self.trades_updated[i]["exit_price"]} entry_price: {self.trades_updated[i]["entry_price"]} profit {self.trades_updated[i]["profit"]} Running Profit: {self.running_profit}')

                    self.email_Text(f'SELLlll ID: {self.trades_updated[i]["ID"]}  exit_price: {self.trades_updated[i]["exit_price"]} profit {self.trades_updated[i]["profit"]}',self.vers)
        
            
    def BUY_MARKET(self):
        print("buy  CALLED and rebalancing is",self.rebalancing)
       
        if self.rebalancing ==1:
            self.SHARES = self.get_shares_to_long()
            order = client.order_market_buy(
            symbol=self.TRADE_SYMBOL,
            quantity=self.SHARES)
            print(order)

            self.rebalancing =0

        else:
            self.SHARES = self.MIN_SHARES
            order = client.order_market_buy(
            symbol=self.TRADE_SYMBOL,
            quantity=self.SHARES)
            print(order)

        self.can_buy = 0



        for obj in order["fills"]:
        
            self.trade_entry_prices.append(float(obj["price"]))
        
        self.entry_price = self.trade_entry_prices[-1]

        

        #make Row
        row = {"ID":self.add_ID(),"entry_date":datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),"exit_date":None,"entry_price":self.entry_price,"exit_price":0,"shares":self.SHARES,"symbol":self.TRADE_SYMBOL,"tp_price": self.tp_price(self.entry_price),"long":1,"short":0,"open":1,"closed":0,"profit":0}

        #write trade to file
        self.write_list_to_file("hedge_TRADES.txt",row)

        #empty trades arry
        
        self.read_list_from_file("hedge_TRADES.txt")

        print(f'BUYYYYYYY ID: {self.trades_updated[-1]["ID"]} date: {self.trades_updated[-1]["entry_date"]} Entry_price: {self.trades_updated[-1]["entry_price"]} TP: {self.trades_updated[-1]["tp_price"]}')
        
        
        self.email_Text(f'BUYYYYYYY ID: {self.trades_updated[-1]["ID"]}  Entry_price: {self.trades_updated[-1]["entry_price"]} TP: {self.trades_updated[-1]["tp_price"]}',self.vers)

    # def on_open(self,ws):
    #     print(' open sesame')
    

    # def on_close(self,ws):
    #     print('closed connection')

#INIT


# def on_message(self,ws,message):
    
#     try:    
#         global closes
#         global CANDLES
#         global STATE
#         global barCount
#         global last_rsi
#         global tick_price
#         global avg_trade_entry_price
#         global trade_entry_prices
#         global trade_ticks
#         global trail_stop_price
#         global EMA1_WINDOW
#         global EMA2_WINDOW
#         global purchased_shares
#         global SELL_QUANTITY
#         global TAKE_PROFIT
#         global avg_trade_exit_price
#         global tickCounter
#         global napper
#         global diff_value
#         global STRAT_DIFF
#         global EMA_to_low_diff
#         global EMA_to_low_diff_short
#         global short_diff_value
#         global hist_bars
#         global indx
#         global stop_index
#         global TRAIL_STOP_VALUE
#         global nap_bar
#         # global ai
   
#         json_message = json.loads(message)
        
#         candle = json_message['k']
        
#         is_candle_closed = candle['x']
        
#         close = float(candle['c'])

#         tick_price = float(candle['c'])

#         # print(CANDLES.items())
#         # print(f'{tick_price} and RSI {last_rsi}')
        
#         # REAL TIME
#         tickCounter +=1  
#         napper +=1
    

#         # if barCount > 1:
#         #     pass
            
#         # #SELL to close
#         #     if STATE["live"] == 1 and STATE["long"] == 1:
#         #         if tick_price > CANDLES[-1]["high_EMA"]:
#         #             if is_item_greater_or_less(CANDLES,"high","high_EMA",">",2):
#         #                 SELL_MARKET()




#         #     #stop to close
#         #     if STATE["live"] == 1 and STATE["long"] == 1:
#         #         if tick_price < avg_trade_entry_price - STOP_LOSS*2.5:
#         #             if STATE["live"] == 1 and STATE["long"] == 1:
#         #                 SELL_MARKET()
            
#         #     # #SHORT
#         #     if CANDLES[-1]["EMA1"] > 0:
#         #         if tick_price > CANDLES[-1]["high_EMA"]:
#         #             #prev high
#         #             if CANDLES[-2]["low_EMA"] > CANDLES[-2]["EMA1"]:
#         #                 if STATE["live"]==0 and STATE["short"]==0:
#         #                     SHORT()


#         # REAT TIME End
#         if is_candle_closed:
#             barCount +=1
#             nap_bar +=1

            
#         #record Data!!!!
#             if barCount > 0:
#                 CANDLES.append({"date": milsToDateTime(json_message['E']), "RSI":last_rsi, "close":float(candle['c']),"open":float(candle['o']),"high":float(candle['h']),"low":float(candle['l']),"volume":float(candle["v"]),"EMA1":0,"EMA2":0,"bar_length":0,"high_EMA":0,"low_EMA":0})
#                 closes.append(float(close))
#                 ai.set_closes(float(close))
#                 EMA3_ai.set_closes(float(close))

#                 #new
#                 # setup()
                

#                 ai.set_highs(CANDLES[-1]["high"])
#                 ai.set_lows(CANDLES[-1]["low"])

#                 #Indictors
#                 high_EMA = ai.get_highs_EMA(2)
#                 low_EMA = ai.get_lows_EMA(2)

#                 if high_EMA > 0 and low_EMA > 0:
#                     CANDLES[-1]["high_EMA"] = high_EMA
#                     CANDLES[-1]["low_EMA"] = low_EMA

                

#                 EMA1 = EMA("EMA1",closes,EMA1_WINDOW)
                
#                 if EMA1 > 0:
#                     CANDLES[-1]["EMA1"] = EMA1
                
#                 EMA2 = EMA("EMA2",closes,EMA2_WINDOW)
                
#                 if EMA2 > 0:
#                     CANDLES[-1]["EMA2"] = EMA2 

#                 if EMA1 > 0:
#                     if CANDLES[-1]["close"] < CANDLES[-1]["EMA1"]: 
#                         if CANDLES[-1]["open"] > CANDLES[-1]["close"]:#redbar
#                             dfference = CANDLES[-1]["EMA1"] - CANDLES[-1]["low"]
#                             CANDLES[-1]['bar_length'] = dfference
#                 #restting
#                 ai.min_tick_lows = []
#                 ai.max_tick_highs = []
            
                

#             #record Data!!!!

#                 #STRATEGY
#                 self.hedge_strat(CANDLES[-1]["close"],CANDLES[-1]["EMA1"])

                
#                 self.print_shit(CANDLES[-1]["close"])

#     except Exception as e:
#         print("THERE IS AN ERROR",e)
            
#     def bot_thread(self):
#         #START
#         ws = websocket.WebSocketApp(self.SOCKET, on_open=self.on_open, on_close=self.on_close, on_message=self.on_message)

#         ws.run_forever()
#     def start_bot_on_thread(self):
#         x = threading.Thread(target=self.bot_thread)
#         x.start()