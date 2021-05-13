import websocket,json,pprint, talib, numpy

from binance.client import Client
from binance.enums import *
import config
import datetime
from helpers import *
import time
import os


STATE = {"live":0,"long":0,"short":0,"games":0,"set_A":0,"set_B":0,"set_C":0,"simulation":0,"history":0,"trailing":0,"double_below":0,"double_above":0,"tick_crossed_below":0,"tick_crossed_above":0,"wins":0,"learns":0}
RSI_PERIOD =14
RSI_OVERBOUGHT =70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'DOGEUSDT'
TRADE_QUANTITY = 1000
SELL_QUANTITY = 1000
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
STOP_LOSS = 0.015

TAKE_PROFIT = .003
diff_value = .003
TRAIL_STOP_VALUE = 0

EMA1_WINDOW = 3
EMA2_WINDOW = 3

purchased_shares  = 0
tickCounter = 0
napper = 0
vers = 'BLSH'
i=0
running_profit = 0
shares = 1000
EMA_to_low_diff_short =0
EMA_to_low_diff =0
STRAT_DIFF = 0
hist_bars = []
indx = None
stop_index = -1

trail_babys = []
nap_bar = 0


#AI
short_diff_value = 0

HISTORY_INTERVAL=Client.KLINE_INTERVAL_1MINUTE
TRADE_INTERVAL = "1m"
SHARES = 1000

foo_email = "3102796480@tmomail.net"
alex_email = "3235594184@vtext.com"

SOCKET = f'wss://stream.binance.com:9443/ws/{TRADE_SYMBOL.lower()}@kline_{TRADE_INTERVAL}'


client = Client(config.API_KEY,config.API_SECRET, tld='us')
class Hedge():
    def __init__(self):
        self.vers = "hedge"
        self.TRADE_SYMBOL = "DOGEUSDT"
        self.trade_entry_prices = []
        self.trade_exit_prices = []
        self.entry_price = 0
        self.exit_price = 0
        self.running_profit = 0
        self.rebalancing = 0
        self.MIN_SHARES = 1000
        self.SHARES = self.MIN_SHARES
        #git
        
        self.TRADES_dict= {"ID":1,"entry_date":datetime.datetime.now(),"exit_date":None,"entry_price":0,"exit_price":0,"shares":0,"symbol":"DOGEUSDT","tp":0,"long":0,"open":0,"closed":0,"profit":0}

        # self.trades = []

        self.trades_updated = []
    
    def print_shit(self,close):
        pass
    
        # print(f'ID: {trade["ID"]} tp: {trade["tp_price"]} ')
        # print(f'unrealized_profits {sum(unrealaized_profits)}')

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
    def read_financials_from_file(self,name):
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
            financials_from_file = temp_array[-1]
            temp_array = []

            
            FILE.close()
            return financials_from_file

    def get_shares_to_short(self):
        row = self.read_financials_from_file("financials.txt")
        return row["shorts_to_buy"]





    def hedge_strat(self,close,EMA_item):
        #SELL
        self.short_close_condition(close)
        print("sleeping")
        time.sleep(4)
        #BUY
        self.short_condition(close,EMA_item)
        

        # 


        
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
                if close <= trade["entry_price"] - trade["entry_price"] *.01:
                    self.SHORT_CLOSE(trade)


    def tp_price(self,entry_price):
        tp_price_ = entry_price - entry_price *.01
        return tp_price_

    def SHORT_CLOSE(self,trade):
        if STATE["simulation"] ==0:
            
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

            
            #write to FOOBASE
            

            #clear memory


            

            
            # email_Text(f'SELLlll ID: {self.trades_updated["ID"]}  exit_price: {self.trades_updated["exit_price"]} profit {self.trades_updated["profit"]}',self.vers)
            



    def SHORT(self):
        try:
            # if STATE["simulation"]==1:
            
            #     avg_trade_entry_price = hist_bars[-1]["close"]

            #     print(f'{hist_bars[-1]["date"]} BUYYYYYYYYY Entrty Price: {avg_trade_entry_price}')

            #state
            if STATE["simulation"]==0:

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
        
       
    def get_highs_EMA(self,window):
        highs_EMA_ = EMA("highs_EMA",self.max_highs,window)
        return highs_EMA_
        
    
    def get_lows_EMA(self,window):
        lows_EMA_ = EMA("lows_EMA",self.max_lows,window)
        return lows_EMA_
    
    def get_tick_EMA(self,tick,window):
        

        self.closes.append(tick)
        tick_EMA_ = EMA("tick_closes_EMA",self.closes,window)
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
        tick_EMA_ = EMA("tick_EMA",self.max_lows,window)
        self.max_lows.pop(-1)
        return tick_EMA_
    def tick_highs_EMA(self,tick,window):
        self.max_tick_highs.append(tick)

        self.max_highs.append(max(self.max_tick_highs))
        tick_EMA_ = EMA("tick_EMA",self.max_highs,window)
        self.max_highs.pop(-1)
        return tick_EMA_

    

def email_Text(sub,msg):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    global foo_email

    email = "redfoo@partyrock.com" # the email where you sent the email
    password = config.GMP
    send_to_email = foo_email # for whom
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

def trail_stop(value):
    global avg_trade_entry_price
    global trade_entry_prices
    global trade_ticks
    global trail_stop_price
    global tick_price
    global STOP_LOSS
    global trade_tick_high
    hello = 2-2

    # print("inside Trail")
    
    
    if tick_price > avg_trade_entry_price:
        # print("passed condition")
    
        trade_ticks.append(tick_price)
        # print("appended")
        trade_tick_high = max(trade_ticks)
        # print()
        trail_stop_price = trade_tick_high - value
    

    return trail_stop_price

def BUY():
    order(sym=TRADE_SYMBOL,side=SIDE_BUY,order_type=ORDER_TYPE_MARKET,quan=TRADE_QUANTITY)
    return true

def BUY_MARKET():
    global STATE
    global trade_entry_prices
    global avg_trade_entry_price
    global purchased_shares
    global trail_stop_price
    global avg_trade_exit_price
    global napper
    global vers
    global CANDLES
    global i
    global running_profit
    global STOP_LOSS
    global hist_bars
    global stop_index
    global nap_bar
    shares=[]


    if STATE["simulation"]==1:
        if STATE["live"]==0 and STATE["long"]==0:
            STATE["live"]=1
            STATE["long"]=1
            stop_index = -1
            avg_trade_entry_price = hist_bars[-1]["close"]

            print(f'{hist_bars[-1]["date"]} BUYYYYYYYYY Entrty Price: {avg_trade_entry_price}')


    
        #state
        if STATE["simulation"]==0:

            #self.TRADES_dict= {"ID":1,"entry_date":datetime.datetime.now(),"exit_date":None,"entry_price":0,"exit_price":0,"shares":0,"symbol":"DOGE","tp":0,"long":0,"open":0,"closed":0,"running_profit":0}
            #self.trades = []

            order = client.order_market_buy(
            symbol=hedge.TRADE_SYMBOL,
            quantity=hedge.SHARES)
            print(order)

            for obj in order["fills"]:
            
                trade_entry_prices.append(float(obj["price"]))
          
            avg_trade_entry_price = trade_entry_prices[-1]

            

            email_Text(f'SOMETHING HERE')
            
        else:
            return

        # for obj in order["fills"][0]:
        #     shares.append(int(obj["qty"]))
        # purchased_shares = int(sum(shares))

def SELL_MARKET():
    global STATE
    global trail_stop_price
    global purchased_shares
    global avg_trade_exit_price
    global avg_trade_entry_price
    global vers
    global trade_entry_prices
    global i
    global running_profit
    global shares
    global hist_bars
    global SHARES
    global stop_index
    global nap_bar
    global napper
    global trade_ticks

    if STATE["simulation"]==1:
        if STATE["live"]==1 and STATE["long"]==1:
            
            STATE["live"]=0
            STATE["long"]=0
            STATE["games"] +=1
            stop_index = -1
            ai.min_tick_lows = []
            ai.max_tick_highs = []


            avg_trade_exit_price = hist_bars[-1]["close"]
            profit = avg_trade_exit_price - avg_trade_entry_price
            if profit > 0:
                STATE["wins"]+=1
            else:
                STATE["learns"]+=1
            running_profit += profit
            print(f'{hist_bars[-1]["date"]} SELLLLLLL EXIT: {avg_trade_exit_price} Profit = {profit} ,GAMES {STATE["games"]}') 
            

    if STATE["simulation"] ==0:
        if STATE["live"]==1 and STATE["long"]==1:
            
            order = client.order_market_sell(
            symbol=TRADE_SYMBOL,
            quantity=SELL_QUANTITY)
            print(order)


            for obj in order["fills"]:
                
                trade_entry_prices.append(float(obj["price"]))
                # print(f'last trade entry price {trade_entry_prices[-1]}')
            # if len(trade_entry_prices) > 1:
            #     avg_trade_exit_price = sum(trade_entry_prices) / len(trade_entry_prices)
            # else:
            avg_trade_exit_price = trade_entry_prices[-1]
            profit = avg_trade_exit_price - avg_trade_entry_price 
            print(f' {datetime.datetime.now()} Exit:{avg_trade_exit_price}', f'PROFIT:{profit} {vers} ')
            
            
            
            running_profit += profit

            
            
            avg_trade_entry_price = 0
            trade_entry_prices = []
            trade_ticks = []
            trail_stop_price = 0

            nap_bar = 0

            STATE["live"]=0
            STATE["long"]=0
            STATE["games"]+=1
            STATE['trailing'] = 0
            stop_index = -1
            ai.min_tick_lows = []
            ai.max_tick_highs = []

            if profit > 0:
                STATE["wins"]+=1
            else:
                STATE["learns"]+=1

            print(f'running prof:{running_profit * SHARES},GAMES {STATE["games"]} WINS:{STATE["wins"]} LEARNS: {STATE["learns"]}')
            
            email_Text(f'SELL CLOSE:{avg_trade_exit_price} W:{STATE["wins"]} L:{STATE["learns"]}',f'RP:{running_profit} ')
            
        else:
            return
def SHORT():
    global STATE
    global trail_stop_price
    global purchased_shares
    global avg_trade_exit_price
    global avg_trade_entry_price
    global vers
    global trade_entry_prices
    global i
    global running_profit
    global shares
    global napper
    global STOP_LOSS

    if STATE["simulation"]==1:
        if STATE["live"]==0 and STATE["short"]==0:
            
            STATE["live"]=1
            STATE["short"]=1

            avg_trade_entry_price = CANDLES[-1]["close"]
            
            
            print(f'{CANDLES[-1]["date"]} SHORTTTTT ENTRY: {avg_trade_entry_price}') 
            

    if STATE["simulation"] ==0:
        if napper >=0:
            if STATE["live"]==0 and STATE["short"]==0:
                napper = 0
                
                    
                order = client.order_market_sell(
                symbol=TRADE_SYMBOL,
                quantity=SELL_QUANTITY)
                print(order)
                STATE["live"]=1
                STATE["short"]=1


                for obj in order["fills"]:
                    
                    trade_entry_prices.append(float(obj["price"]))
                    # print(f'last trade entry price {trade_entry_prices[-1]}')
                # if len(trade_entry_prices) > 1:
                #     avg_trade_exit_price = sum(trade_entry_prices) / len(trade_entry_prices)
                # else:
                avg_trade_entry_price = trade_entry_prices[-1]
                STOP_LOSS = avg_trade_entry_price - CANDLES[-1]["EMA1"]
                print(f'SHORT   {avg_trade_entry_price} @ {datetime.datetime.now()} STATE: {STATE["live"]} , {STATE["short"]} ')
                


                profit = avg_trade_entry_price - avg_trade_exit_price 
                email_Text(f'SHORT ENTRY:{avg_trade_entry_price}', "Moon")
                
                
                
                # print("Sleeping")
                # time.sleep(2)
            else:
                return
def SHORT_CLOSE():
    global STATE
    global trade_entry_prices
    global avg_trade_entry_price
    global purchased_shares
    global trail_stop_price
    global avg_trade_exit_price
    global napper
    global vers
    global CANDLES
    global i
    global running_profit
    shares=[]


    if STATE["simulation"]==1:
        if STATE["live"]==1 and STATE["short"]==1:
            STATE["live"]=0
            STATE["short"]=0
            avg_trade_exit_price = CANDLES[-1]["close"]
            profit = avg_trade_entry_price - avg_trade_exit_price

            running_profit += profit

            print(f'{CANDLES[-1]["date"]} SHORT CLOSEDDD EXIT : {avg_trade_exit_price} profit {profit}')



    if STATE["live"]==1 and STATE["short"]==1:
        #state
        if STATE["simulation"]==0:

            
            if napper >= 0:
                order = client.order_market_buy(
                symbol=TRADE_SYMBOL,
                quantity=TRADE_QUANTITY)
                print(order)
                STATE["live"]=0
                STATE["short"]=0

                for obj in order["fills"]:
                
                    trade_entry_prices.append(float(obj["price"]))
                # print(f'last trade entry price {trade_entry_prices[-1]}')
            # if len(trade_entry_prices) > 1:
            #     avg_trade_entry_price = sum(trade_entry_prices) / len(trade_entry_prices)
            # else:
                avg_trade_exit_price = trade_entry_prices[-1]
                profit = avg_trade_entry_price - avg_trade_exit_price
                
                print(f'{CANDLES[-1]["date"]} SHORT CLOSEDDD EXIT: {avg_trade_exit_price} profit: {profit}')


                email_Text(f'SHRT_CLOSE {avg_trade_exit_price}', f'EXIT : profit {profit}')
                avg_trade_entry_price = 0
                trade_entry_prices = []
                trade_ticks = []
                trail_stop_price = 0
                

                
            else:
                return

        

def SELL():
    order(sym=TRADE_SYMBOL,side=SIDE_SELL,order_type=ORDER_TYPE_MARKET,quan=TRADE_QUANTITY)
    return True

#indicaters
def EMA(name,list,window):
    if len(list) > window:
        np_closes1 = numpy.array(list)
        ema = talib.EMA(np_closes1, window)
        # print(f'{name} first value is {ema[-1]}')
        return ema[-1]
    else:
        return 0

def doji(hl,oc,pos):
    diffHL = CANDLES[pos]["high"] - CANDLES[pos]["low"]
    diffOC = CANDLES[pos]["close"] - CANDLES[pos]["open"] 
    doji = abs(diffHL) >= hl and abs(diffOC) <= oc
    return doji

def close_above_2_Emas(EMA1,EMA2):
    bullish = CANDLES[-1]['close'] > EMA1 and CANDLES[-1]['close'] > EMA2
    return bullish



def order(sym, side=SIDE_BUY,order_type=ORDER_TYPE_MARKET,quan=1):
    try:
        print("sending order...")
        order = client.create_test_order(symbol=sym, side=side, type=order_type, quantity=quan)
        print(order)
    except Exception as e:
        return False
    return True

def tick_below_x(candle_pos,candle_val):
    tick_below_ = tick_price < CANDLES[candle_pos][candle_val]
    return tick_below_
def a_below_b(a_candle_pos,a_candle_val,b_candle_pos,b_candle_val):
    a_below_b_ = CANDLES[a_candle_pos][a_candle_val] < CANDLES[b_candle_pos][b_candle_val]
    return a_below_b_

def diff_candle_to_tick(candle_pos,candle_val):
    diff_candle_to_tick_ = CANDLES[candle_pos][candle_val] - tick_price
    return diff_candle_to_tick_

def diff_a_to_b(a_candle_pos,a_candle_val,b_candle_pos,b_candle_val):
    diff_a_to_b_ = CANDLES[a_candle_pos][a_candle_val] - CANDLES[b_candle_pos][b_candle_val]
    return diff_a_to_b_
def diff_any_2_vals(a,b):
    return a-b

def is_tick_greater_or_less(tick,list_,item,operator,start,stop):
    count = 0
    

    for i in range(start,stop,-1):

        if operator == ">":
            if tick > list_[i][item]:
                if is_green_bar(list_,i):
                
                    count+=1
                else:
                    pass
        if operator == "<":
            # print(tick,"vs",list_[i][item],i)
            
            if tick < list_[i][item]:
                
                count+=1
            else:
                pass
        if operator == "<red":
            # print(tick,"vs",list_[i][item],i)
            
            if tick < list_[i][item]:
                if is_green_bar(list_,i) == False:
                    count+=1
            else:
                pass
        

        if count > 0:
            # print("count is ",count)
            count =0
            return True
        
        


        
def is_item_greater_or_less(list_,item1,item2,operator,start,stop,target):
    count = 0
    stop = stop_index
    print("func called")
   

    for i in range(-1,stop,-1):
        
        
        if i >= stop:
            print("iiiiiiiii",i,"stop:",stop)

            if operator == ">":
                if list_[i][item1] > list_[i][item2]:
                    
                    count+=1
            if operator == ">green":
                if list_[i][item1] > list_[i][item2]:
                    if is_green_bar(list_,i):
                        count+=1
                
            if operator == "<":
                if list_[i][item1] < list_[i][item2]:
                    
                    
                    # if is_green_bar(list_,i) == False:
                    count+=1
            if operator == "<red":
                if list_[i][item1] < list_[i][item2]:
                    
                    
                    if is_green_bar(list_,i) == False:
                        count+=1
            
                
            
            
            if count == target:
                print("TARGET REACHED",i)
                count = 0
                return i
        else:
            count = 0
            return 


        
def is_entry_cross_below(tick,list_):
    
    tick_ =tick
    cross_counter = 0
    done = False
    index = 0
    listy = list_
    if is_tick_greater_or_less(tick_,listy,"low_EMA","<",1,-1):
        # print("is_tick_greater_or_less",is_tick_greater_or_less(tick_,listy,"low_EMA","<",1,-1),listy[-1]["date"])

        
        index_for_for_next = is_item_greater_or_less(listy,"low","low_EMA",">",-1,-9,target=3)
        if index_for_for_next == False:
            print("INDEX FOR NEXT","falseee")
            return False
        else: 
            index=index_for_for_next
            # print("INDEX FOR NEXT",index)
    if index == 0:
        if is_double_below(index):
            return True
        else:
            return False


def is_double_below(list_,i):
    
    # return hist_bars[i]["high_EMA"] < hist_bars[i]["EMA1"] #HISTORY
    return list_[i]["high_EMA"] < list_[i]["EMA1"]

def is_double_above(list_,i):
    return list_[i]["low_EMA"] > list_[i]["EMA1"]

def is_green_bar(list_,indx):
    if list_[indx]["open"] < list_[indx]["close"]:
        return True
    else: 
        return False

def trail_baby(tick,stop,thresh_item,dir):
    global avg_trade_entry_price
    global trade_entry_prices
    global trade_ticks
    global trail_stop_price
    global tick_price
    global STOP_LOSS
   
    global STATE
    hello = 2-2


    # print("inside Trail")
    if STATE["trailing"]:
        print("TRAILING",trail_stop_price)
        if dir == "<":
            if tick < thresh_item:
                # print("passed condition")
            
                trade_ticks.append(tick)
                # print("appended")
                trade_tick_low = min(trade_ticks)
                # print()
                trail_stop_price = trade_tick_low + stop
        if dir == ">":
            if tick > thresh_item:
                # print("passed condition")
            
                trade_ticks.append(tick)
                # print("appended")
                trade_tick_high = max(trade_ticks)
                # print()
                trail_stop_price = trade_tick_high + (-1*stop)
        

        return trail_stop_price
def long_reversal_3EMA(tick):
    close = CANDLES[-1]["close"]
    prev_close = CANDLES[-2]["close"]


    EMA_3 = CANDLES[-1]["EMA1"] # EMA 3
    prev_EMA_3 = CANDLES[-2]["EMA1"]

    EMA_8 = CANDLES[-1]["EMA2"]
    prev_EMA_8 = CANDLES[-2]["EMA2"] #EMA 8

    open_ = CANDLES[-1]["open"]

    if tick < close + (-1* tick/1550):
        if open_ < EMA_3 and close >= EMA_3:
            if prev_close < prev_EMA_3 and prev_close < prev_EMA_8:
                if prev_EMA_3 < prev_EMA_8:
                    return True
                else:
                    return False
            

def short_reversal_3EMA(tick):
    close = CANDLES[-1]["close"]
    prev_close = CANDLES[-2]["close"]

    EMA_3 = CANDLES[-1]["EMA1"] # EMA 3
    prev_EMA_3 = CANDLES[-2]["EMA1"]

    EMA_8 = CANDLES[-1]["EMA2"]
    prev_EMA_8 = CANDLES[-2]["EMA2"] #EMA 8
    
    open_ = CANDLES[-1]["open"]

    if tick > close + .0002:
        if open_ > EMA_3 and close <= EMA_3:
            if prev_close > prev_EMA_3 and prev_close > prev_EMA_8:
                return True


def buy_low_sell_high(tick,low_item,high_item,EMA_item,EMA_item2):
    global STATE
    global CANDLES

    #signals
    # tick_below_2_EMAs = tick < EMA_item and tick < EMA_item2
    # if tick_below_2_EMAs:
    #     print("tick_below_2_EMAs")
    #     print("EMA ITEM",EMA_item)
    #     print("EMA ITEM2",EMA_item2)

    #     print("EMA2",CANDLES[-1]["EMA2"])
    #     print(tick)
    # tick_above_2_EMAs = tick > EMA_item and tick > EMA_item2
    # if tick_above_2_EMAs:

    #     print("tick_above_2_EMAs")
    #     print("EMA ITEM",EMA_item)
    #     print("EMA ITEM2",EMA_item2)

    #     print("EMA2",CANDLES[-1]["EMA2"])
    #     print(tick)
    
    #sell
    if tick > high_item:
        if CANDLES[-1]["EMA2"] > CANDLES[-1]["EMA1"]:
            print("SELL SIGNAL")
            ai.min_tick_lows = []
            ai.max_tick_highs = []
            
            if STATE["live"]==1 and STATE["long"] ==1:
                SELL_MARKET()

    # if tick < EMA_item and tick < EMA_item2:
    #     if EMA_item2 < EMA_item:
    #         if CANDLES[-1]["EMA2"] > CANDLES[-1]["EMA1"]:
    #             print("SELL SIGNAL")
    #             ai.min_tick_lows = []
    #             ai.max_tick_highs = []

    #             if STATE["live"]==1 and STATE["long"] ==1:
    #                 SELL_MARKET()
            
    
        

    #buy
    if tick < low_item:
        # if CANDLES[-1]["high_EMA"] < CANDLES[-1]["EMA1"]:
        if CANDLES[-1]["EMA2"] < CANDLES[-1]["EMA1"]:
            print("BUY SIGNAL")
            ai.min_tick_lows = []
            ai.max_tick_highs = []

            if STATE["live"]==0 and STATE["long"] ==0:
                BUY_MARKET()
    # if tick > EMA_item and tick > EMA_item2:
    #     if EMA_item2 > EMA_item:
    #         if CANDLES[-1]["EMA2"] < CANDLES[-1]["EMA1"]:
    #             print("BUY SIGNAL")
    #             ai.min_tick_lows = []
    #             ai.max_tick_highs = []

    #             if STATE["live"]==0 and STATE["long"] ==0:
    #                 BUY_MARKET()
            

    
    #Sell
    









#init funcs
ai = AI()
EMA3_ai = AI()
ai_diff = AI()

hedge = Hedge()

hedge.read_list_from_file("hedge_TRADES.txt")


#ARRAYS
# CANDLE_DIFFS = ARR()

print("Initialized AI")

# def setup():
#     global CANDLES
#     #diff shit
    
#     ai_diff.set_diff_of_abs(ai_diff.diff_of_ab(CANDLES[-1]["EMA1"],CANDLES[-1]["low_EMA"]))

#     CANDLE_DIFFS.arr.append(EMA("diffs_EMA",ai_diff.diff_of_abs,5))


###################################### GET HISTORY BARS

historical_bars = client.get_historical_klines(TRADE_SYMBOL, HISTORY_INTERVAL, "1 day ago UTC")
# historical_bars = client.get_historical_klines("DOGEUSDT", Client.KLINE_INTERVAL_1MINUTE, "21 Apr, 2021", "")

hist_bars = []
length_list = []
for bar in historical_bars:
    CANDLES.append({"date": milsToDateTime(bar[0]), "close":float(bar[4]),"open":float(bar[1]),"high":float(bar[2]),"low":float(bar[3]),"volume":float(bar[5]),"RSI":0,"EMA1":0,"EMA2":0,"bar_length":0,"high_EMA":0,"low_EMA":0})
    
    closes.append(float(bar[4]))
    ai.set_closes(float(bar[4]))
    EMA3_ai.set_closes(float(bar[4]))

    # setup()
    #Indictors

    ai.set_highs(CANDLES[-1]["high"])
    ai.set_lows(CANDLES[-1]["low"])

            #Indictors
    high_EMA = ai.get_highs_EMA(2)
    low_EMA = ai.get_lows_EMA(2)

    if high_EMA > 0 and low_EMA > 0:
        CANDLES[-1]["high_EMA"] = high_EMA
        CANDLES[-1]["low_EMA"] = low_EMA



    EMA1 = EMA("EMA1",closes,EMA1_WINDOW)
    if EMA1 > 0:
        CANDLES[-1]["EMA1"] = EMA1
    
    EMA2 = EMA("EMA2",closes,EMA2_WINDOW)
    
    if EMA2 > 0:
        CANDLES[-1]["EMA2"] = EMA2
    #length bar
    if EMA1 > 0:
        if CANDLES[-1]["close"] < CANDLES[-1]["EMA1"]: 
            if CANDLES[-1]["open"] > CANDLES[-1]["close"]:#redbar
                dfference = CANDLES[-1]["EMA1"] - CANDLES[-1]["low"]
                CANDLES[-1]['bar_length'] = dfference
                length_list.append(dfference)

#popping out bad bar
CANDLES.pop(-1)
closes.pop(-1)
ai.closes.pop(-1)
ai.max_highs.pop(-1)
ai.max_lows.pop(-1)
EMA3_ai.closes.pop(-1)

#resetting
ai.min_tick_lows = []
ai.max_tick_highs = []


#STATIC STUFF
# for diff_EMA in CANDLE_DIFFS.arr:
#     print(f'EMA1 to Low EMA {diff_EMA}')  

# for CAN in CANDLES:
#     print(f' Date: {CAN["date"]} CLOSE: {CAN["close"]} EMA1: {CAN["EMA1"]} EMA2: {CAN["EMA2"]}, high_EMA: {CAN["low_EMA"]} ENTRY: {avg_trade_entry_price}')
# print(len(CANDLES))
# print(len(closes))
###################################### GET HISTORY BARS


#SIMULATION STRATS WITH BUYS/SELLS                
                
if STATE["simulation"]==1 and STATE["history"]==1:
    for i in range(len(CANDLES)):

        hist_bars.append(CANDLES[i])


    # Sell
        if STATE["live"]==1 and STATE["long"]==1:
            
            # print(hist_bars[-1]["close"],avg_trade_entry_price) 610

            if is_tick_greater_or_less(hist_bars[-1]["high"],hist_bars,"high_EMA",">",-1,-2):
                indx = is_item_greater_or_less(hist_bars,"high","high_EMA",">green",-1,stop=stop_index,target=3)
                if indx != None and indx < -1:
                    # if is_double_above(CANDLES,indx+-1) == True:
                    SELL_MARKET() 
            
            if is_tick_greater_or_less(hist_bars[-1]["low"],hist_bars,"low_EMA","<red",-1,-2):
                indx = is_item_greater_or_less(hist_bars,"low","low_EMA","<red",-1,stop=stop_index,target=4)
                if indx != None and indx < -1:
                    print("REDDDDDD SELL")
                    SELL_MARKET() 


        if hist_bars[-1]["EMA1"] > 0:
            stop_index -=1
            if STATE["live"]==0 and STATE["long"]==0:
            # print(hist_bars[-1]["date"],hist_bars[-1]["close"])
                if is_tick_greater_or_less(hist_bars[-1]["low"],hist_bars,"low_EMA","<",-1,-2):
                    # print("passed 1")
                    indx = is_item_greater_or_less(hist_bars,"low","low_EMA","<",-1,stop=stop_index,target=2)
                    if indx != None and indx < -1:
                        
                        if is_double_below(hist_bars,indx+-1) == True:
                        #     print(hist_bars[indx+-1]["date"],hist_bars[indx+-1]["close"])
                            # print(hist_bars[indx]["date"],hist_bars[indx]["close"],indx)
                            
                            
                            # print("passed 2",is_item_greater_or_less(hist_bars,"low","low_EMA",">",-1,-9,target=3))
                            if STATE["live"]==0 and STATE["long"]==0:
                                BUY_MARKET()

     
    print(f'running prof:{running_profit * SHARES},GAMES {STATE["games"]} WINS:{STATE["wins"]} LEARNS: {STATE["learns"]}')
            
            # if hist_bars[-1]["close"] > avg_trade_entry_price + .0025:
            #     SELL_MARKET()
                
            # if hist_bars[-1]["close"] < avg_trade_entry_price - .004:
            #     SELL_MARKET()
                

  

def on_open(ws):
    print(' open sesame')
    

def on_close(ws):
    print('closed connection')

#INIT


def on_message(ws,message):
    
    try:    
        global closes
        global CANDLES
        global STATE
        global barCount
        global last_rsi
        global tick_price
        global avg_trade_entry_price
        global trade_entry_prices
        global trade_ticks
        global trail_stop_price
        global EMA1_WINDOW
        global EMA2_WINDOW
        global purchased_shares
        global SELL_QUANTITY
        global TAKE_PROFIT
        global avg_trade_exit_price
        global tickCounter
        global napper
        global diff_value
        global STRAT_DIFF
        global EMA_to_low_diff
        global EMA_to_low_diff_short
        global short_diff_value
        global hist_bars
        global indx
        global stop_index
        global TRAIL_STOP_VALUE
        global nap_bar
        # global ai
       

    
        json_message = json.loads(message)
        
        candle = json_message['k']
        
        is_candle_closed = candle['x']
        
        close = float(candle['c'])

        tick_price = float(candle['c'])

        # print(CANDLES.items())
        # print(f'{tick_price} and RSI {last_rsi}')
        
        # REAL TIME
        tickCounter +=1  
        napper +=1
    

        # if barCount > 1:
        #     pass
            
        # #SELL to close
        #     if STATE["live"] == 1 and STATE["long"] == 1:
        #         if tick_price > CANDLES[-1]["high_EMA"]:
        #             if is_item_greater_or_less(CANDLES,"high","high_EMA",">",2):
        #                 SELL_MARKET()




        #     #stop to close
        #     if STATE["live"] == 1 and STATE["long"] == 1:
        #         if tick_price < avg_trade_entry_price - STOP_LOSS*2.5:
        #             if STATE["live"] == 1 and STATE["long"] == 1:
        #                 SELL_MARKET()
            
        #     # #SHORT
        #     if CANDLES[-1]["EMA1"] > 0:
        #         if tick_price > CANDLES[-1]["high_EMA"]:
        #             #prev high
        #             if CANDLES[-2]["low_EMA"] > CANDLES[-2]["EMA1"]:
        #                 if STATE["live"]==0 and STATE["short"]==0:
        #                     SHORT()


        # REAT TIME End
        if is_candle_closed:
            barCount +=1
            nap_bar +=1

            
        #record Data!!!!
            if barCount > 0:
                CANDLES.append({"date": milsToDateTime(json_message['E']), "RSI":last_rsi, "close":float(candle['c']),"open":float(candle['o']),"high":float(candle['h']),"low":float(candle['l']),"volume":float(candle["v"]),"EMA1":0,"EMA2":0,"bar_length":0,"high_EMA":0,"low_EMA":0})
                closes.append(float(close))
                ai.set_closes(float(close))
                EMA3_ai.set_closes(float(close))

                #new
                # setup()
                

                ai.set_highs(CANDLES[-1]["high"])
                ai.set_lows(CANDLES[-1]["low"])

                #Indictors
                high_EMA = ai.get_highs_EMA(2)
                low_EMA = ai.get_lows_EMA(2)

                if high_EMA > 0 and low_EMA > 0:
                    CANDLES[-1]["high_EMA"] = high_EMA
                    CANDLES[-1]["low_EMA"] = low_EMA

                

                EMA1 = EMA("EMA1",closes,EMA1_WINDOW)
                
                if EMA1 > 0:
                    CANDLES[-1]["EMA1"] = EMA1
                
                EMA2 = EMA("EMA2",closes,EMA2_WINDOW)
                
                if EMA2 > 0:
                    CANDLES[-1]["EMA2"] = EMA2 

                if EMA1 > 0:
                    if CANDLES[-1]["close"] < CANDLES[-1]["EMA1"]: 
                        if CANDLES[-1]["open"] > CANDLES[-1]["close"]:#redbar
                            dfference = CANDLES[-1]["EMA1"] - CANDLES[-1]["low"]
                            CANDLES[-1]['bar_length'] = dfference
                #restting
                ai.min_tick_lows = []
                ai.max_tick_highs = []
            
                

            #record Data!!!!

                #STRATEGY
                hedge.hedge_strat(CANDLES[-1]["close"],CANDLES[-1]["EMA1"])

                

                print("from MEMory",len(hedge.trades_updated))

                print(f' Date: {CANDLES[-1]["date"]} CLOSE: {CANDLES[-1]["close"]} EMA1: {CANDLES[-1]["EMA1"]}')
                hedge.print_shit(CANDLES[-1]["close"])

        # if tickCounter % 15 == 0:

        #     print(f'last high EMA {CANDLES[-1]["high_EMA"]}')  
        #     print(f'tick high EMA: {ai.tick_highs_EMA(tick_price,2)}')
        #     print(f'highs ARRAY lenth {len(ai.max_highs)}')
        #     print(f'tick {tick_price}')
        #     print("------------------")
        #     print(f'last low EMA {CANDLES[-1]["low_EMA"]}')  
        #     print(f'tick low EMA: {ai.tick_lows_EMA(tick_price,2)}')
        #     print(f'lows ARRAY lenth {len(ai.max_lows)}')
        #     print(f'tick {tick_price}')
        #     print(f'tick EMA { ai.get_tick_EMA(tick_price,8)}')
        #     print("00000000000000000000")


        #BUY AND SELL
        # print(CANDLES[-1]["high_EMA"],CANDLES[-1]["EMA1"])
        # if CANDLES[-1]["high_EMA"] < CANDLES[-1]["EMA1"]:
        #     print("condition met")
        # buy_low_sell_high(tick_price,ai.tick_lows_EMA(tick_price,2),ai.tick_highs_EMA(tick_price,2),ai.get_tick_EMA(tick_price,EMA1_WINDOW),EMA3_ai.get_tick_EMA(tick_price, EMA2_WINDOW))
         
        # if barCount > 1:
            
            # SL stop to close 3a
            # if STATE["live"] == 1 and STATE["long"] == 1:
            #     if tick_price < avg_trade_entry_price - tick_price *.003:   
            #         SELL_MARKET()

            #REAL TiME
            


            # if STATE["live"] == 1 and STATE["long"] == 1:
            #     print(f'trail {trail_stop(avg_trade_entry_price *.0065)}') 
            #     print(f'tick {tick_price}')

            #     if tick_price > avg_trade_entry_price + tick_price *.0065:
            #         SELL_MARKET()
                    
            #     if tick_price < trail_stop(avg_trade_entry_price *.0065):
            #         print("TRAIL STOPPPPed OUT")
            #         SELL_MARKET()

            






            #BUY MARKET 1
            # if CANDLES[-1]["EMA2"] > 0:          
            #     if long_reversal_3EMA(tick_price):
            #         if STATE["live"]==0 and STATE["long"]==0:
            #             BUY_MARKET()


            #         print("BUYYYYYY")
            #         STATE["live"] = 1
            #         STATE["long"] = 1
            #         STATE["trailing"] = 0

            # print(f'tick {tick_price} vs trail {trail_stop_price}')
                

                # # if STATE["simulation"]==1 and STATE["history"]==1:
                # #     for i in range(len(CANDLES)):
                # #         hist_bars.append(CANDLES[i])

                # if STATE["live"]==1 and STATE["long"]==1:
                #     # print(hist_bars[-1]["close"],avg_trade_entry_price) 610

                #     if is_tick_greater_or_less(CANDLES[-1]["high"],CANDLES,"high_EMA",">",-1,-2):
                #         indx = is_item_greater_or_less(CANDLES,"high","high_EMA",">green",-1,stop=stop_index,target=3)
                #         if indx != None and indx < -1:
                #             # if is_double_above(CANDLES,indx+-1) == True:
                #             SELL_MARKET() 
            
                #     if is_tick_greater_or_less(CANDLES[-1]["low"],CANDLES,"low_EMA","<red",-1,-2):
                #         indx = is_item_greater_or_less(CANDLES,"low","low_EMA","<red",-1,stop=stop_index,target=4)
                #         if indx != None and indx < -1:
                #             print("REDDDDDD SELL")
                #             SELL_MARKET() 
                        
                #BUY RT 
        # if barCount > 1:      
        #     if CANDLES[-1]["EMA1"] > 0:
        #         if STATE["live"]==0 and STATE["long"]==0:
                    
        #         # print(hist_bars[-1]["date"],hist_bars[-1]["close"])
        #             if is_tick_greater_or_less(tick_price,CANDLES,"low_EMA","<",-1,-2):
        #                 # print("passed 1")
        #                 indx = is_item_greater_or_less(CANDLES,"low","low_EMA","<",-1,-9,target=2)
        #                 if indx != None and indx < -1:
                            
        #                     if is_double_below(CANDLES,indx+-1) == True:
        #                     #     print(hist_bars[indx+-1]["date"],hist_bars[indx+-1]["close"])
        #                         # print(hist_bars[indx]["date"],hist_bars[indx]["close"],indx)
                                
                                
        #                         # print("passed 2",is_item_greater_or_less(hist_bars,"low","low_EMA",">",-1,-9,target=3))
        #                         if STATE["live"]==0 and STATE["long"]==0:
        #                             BUY_MARKET()
        #trail entry below low_ema

        




        
    # Sell
        


            

                
            #BUY MARKET 
           
            # if CANDLES[-1]["EMA1"] > 0:
            #     if is_entry_cross_below(tick_price):
            #         if STATE["live"]==0 and STATE["long"]==0:
            #             BUY_MARKET()


                
            # #TP SHORT CLOSE 
            # if STATE["live"]==1 and STATE["short"]==1:
            #     if tick_price < CANDLES[-1]["low_EMA"]:
            #         #prev bar
            #         if CANDLES[-2]["high_EMA"] < CANDLES[-2]["EMA1"]:
            #             if STATE["live"]==1 and STATE["short"]==1:
            #                 SHORT_CLOSE()
            # #SL SHORT CLOSE
            # if STATE["live"]==1 and STATE["short"]==1:
            #     if tick_price > avg_trade_entry_price + STOP_LOSS*2.5:
            #         if STATE["live"]==1 and STATE["short"]==1:
            #             print("short close STOP loss value is",STOP_LOSS)
            #             SHORT_CLOSE()

            
            
           

    except Exception as e:
        print("THERE IS AN ERROR",e)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)

ws.run_forever()
