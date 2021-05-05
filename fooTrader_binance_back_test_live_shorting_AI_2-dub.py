import websocket,json,pprint, talib, numpy

from binance.client import Client
from binance.enums import *
import config
import datetime
from helpers import *
import time

SOCKET = "wss://stream.binance.com:9443/ws/dogeusdt@kline_1m"
STATE = {"live":0,"long":0,"short":0,"games":0,"set_A":0,"set_B":0,"set_C":0,"simulation":1,"history":1,"trailing":0,"double_below":0,"double_above":0,"tick_crossed_below":0,"tick_crossed_above":0,"wins":0,"learns":0}
RSI_PERIOD =14
RSI_OVERBOUGHT =70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'DOGEUSDT'
TRADE_QUANTITY = 88
SELL_QUANTITY = 88
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
TRAIL_STOP_VALUE = .003

EMA1_WINDOW = 8
EMA2_WINDOW = 20

purchased_shares  = 0
tickCounter = 0
napper = 0
vers = 'AIBUY'
i=0
running_profit = 0
shares =10000
EMA_to_low_diff_short =0
EMA_to_low_diff =0
STRAT_DIFF = 0
hist_bars = []

#AI
short_diff_value = 0


client = Client(config.API_KEY,config.API_SECRET, tld='us')


class AI():
    def __init__(self):
        #arrays
        self.max_highs = []
        self.max_lows = []
        print("Init success")

    
        
        # self.SOCKET = f'wss://stream.binance.com:9443/ws/{self.TRADE_SYMBOL}@kline_{self.INTERVAL}'
        
        #GLOBALS
        
        
       
    def get_highs_EMA(self,window):
        highs_EMA_ = EMA("highs_EMA",self.max_highs,window)
        print("from ai highEMAS",highs_EMA_)
        return highs_EMA_
    
    def get_lows_EMA(self,window):
        lows_EMA_ = EMA("lows_EMA",self.max_lows,window)
        print("from ai lowEMAS",lows_EMA_)
        return lows_EMA_
        

    def set_highs(self,high):
        self.max_highs.append(high)

    def set_lows(self,low):
        self.max_lows.append(low)
    



def email_Text(sub,msg):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    email = "redfoo@partyrock.com" # the email where you sent the email
    password = config.GMP
    send_to_email = "3102796480@tmomail.net" # for whom
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
    shares=[]


    if STATE["simulation"]==1:
        if STATE["live"]==0 and STATE["long"]==0:
            STATE["live"]=1
            STATE["long"]=1
            avg_trade_entry_price = hist_bars[-1]["close"]

            print(f'{hist_bars[-1]["date"]} BUYYYYYYYYY Entrty Price: {avg_trade_entry_price}')


    if STATE["live"]==0 and STATE["long"]==0:
        #state
        if STATE["simulation"]==0:
            
            napper = 0
            order = client.order_market_buy(
            symbol=TRADE_SYMBOL,
            quantity=TRADE_QUANTITY)
            print(order)
            STATE["live"]=1
            STATE["long"]=1

            for obj in order["fills"]:
            
                trade_entry_prices.append(float(obj["price"]))
            # print(f'last trade entry price {trade_entry_prices[-1]}')
        # if len(trade_entry_prices) > 1:
        #     avg_trade_entry_price = sum(trade_entry_prices) / len(trade_entry_prices)
        # else:
            avg_trade_entry_price = trade_entry_prices[-1]

            STOP_LOSS = CANDLES[-1]["EMA1"] - avg_trade_entry_price
            trail_stop_price = avg_trade_entry_price - TRAIL_STOP_VALUE
            print(f'ENTRY  {avg_trade_entry_price} @ {datetime.datetime.now()} Trail: {trail_stop_price} STATE: {STATE["live"]} , {STATE["long"]} ')

            email_Text(f'BUY ENTRY {avg_trade_entry_price}', f' diff {STRAT_DIFF} ')
            
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

    if STATE["simulation"]==1:
        if STATE["live"]==1 and STATE["long"]==1:
            
            STATE["live"]=0
            STATE["long"]=0
            STATE["games"] +=1


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
            if napper > 10:
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
                
                
                email_Text(f'SELL CLOSE:{avg_trade_exit_price}', f'PROFIT:{profit} ')
                
                avg_trade_entry_price = 0
                trade_entry_prices = []
                trade_ticks = []
                trail_stop_price = 0
                STATE["live"]=0
                STATE["long"]=0
                STATE["games"]+=1
                STATE['trailing'] = 0
                print("Sleeping")
                time.sleep(2)
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
        if napper > 30:
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

            
            if napper > 10:
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
                
                count+=1
            else:
                pass
        if operator == "<":
            # print(tick,"vs",list_[i][item],i)
            
            if tick < list_[i][item]:
                
                count+=1
            else:
                pass
        

        if count > 0:
            # print("count is ",count)
            count =0
            return True
        
        


        
def is_item_greater_or_less(list_,item1,item2,operator,start,stop,target):
    count = 0
   

    for i in range(-1,-9,-1):
        print("iiiiiiiii",i)

        if operator == ">":
            if list_[i][item1] > list_[i][item2]:
                count+=1
            
        if operator == "<":
            if list_[i][item1] < list_[i][item2]:
                
                count+=1
            
        
        
        if count == target:
            print("TARGET REACHED",i)
            target = 0
            return i
        
        
            
        
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


def is_double_below(i):
    return hist_bars[i]["high_EMA"] < hist_bars[i]["EMA1"]



    


            
        
    # if count == times:
    #     print("true")
    #     return True
    # else:
    #     print("false",tick)
    #     return False
   


#init funcs
ai = AI()
print("Initialized AI")

###################################### GET HISTORY BARS
if STATE["simulation"]==1 and STATE["history"]==1:
    historical_bars = client.get_historical_klines("DOGEUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    # historical_bars = client.get_historical_klines("DOGEUSDT", Client.KLINE_INTERVAL_1MINUTE, "21 Apr, 2021", "")

    hist_bars = []
    length_list = []
    for bar in historical_bars:
        CANDLES.append({"date": milsToDateTime(bar[0]), "close":float(bar[4]),"open":float(bar[1]),"high":float(bar[2]),"low":float(bar[3]),"volume":float(bar[5]),"RSI":0,"EMA1":0,"EMA2":0,"bar_length":0,"high_EMA":0,"low_EMA":0})
        
        closes.append(float(bar[4]))
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

    for i in range(len(CANDLES)):
        hist_bars.append(CANDLES[i])
        

        if hist_bars[-1]["EMA1"] > 0:
            # print(hist_bars[-1]["date"],hist_bars[-1]["close"])
            if is_tick_greater_or_less(hist_bars[-1]["low"],hist_bars,"low_EMA","<",-1,-4):
                # print("passed 1")
                indx = is_item_greater_or_less(hist_bars,"low","low_EMA",">",-1,-9,target=2)
                if indx != None and indx < -1:
                    
                    if is_double_below(indx+-1) == True:
                        print(hist_bars[indx+-1]["date"],hist_bars[indx+-1]["close"])
                        # print(hist_bars[indx]["date"],hist_bars[indx]["close"],indx)
                        
                        
                        # print("passed 2",is_item_greater_or_less(hist_bars,"low","low_EMA",">",-1,-9,target=3))
                        if STATE["live"]==0 and STATE["long"]==0:
                            BUY_MARKET()

            
            
        # Sell
            if STATE["live"]==1 and STATE["long"]==1:
                # print(hist_bars[-1]["close"],avg_trade_entry_price)
                
                if hist_bars[-1]["close"] > avg_trade_entry_price + .0025:
                    SELL_MARKET()
                    
                if hist_bars[-1]["close"] < avg_trade_entry_price - .004:
                    SELL_MARKET()
                    


        
    print(f'running prof:{running_profit * 1},GAMES {STATE["games"]} WINS:{STATE["wins"]} LEARNS: {STATE["learns"]}')

# avg_length = sum(length_list) / len(length_list)
# max_length = max(length_list)

# print(f'avg: {avg_length} ')
# print(f'max: {max_length} ')

###################################### GET HISTORY BARS

    
    # print(CANDLES[-1]["close"])
    #Indictors
    # EMA1 = EMA("EMA1",closes,EMA1_WINDOW)
    
    # if EMA1 > 0:
    #     CANDLES[-1]["EMA1"] = EMA1
    
    # EMA2 = EMA("EMA2",closes,EMA2_WINDOW)
    
    # if EMA2 > 0:
    #     CANDLES[-1]["EMA2"] = EMA2 

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
       

    
        json_message = json.loads(message)
        
        candle = json_message['k']
        
        is_candle_closed = candle['x']
        
        close = float(candle['c'])

        tick_price = float(candle['c'])

        # print(CANDLES.items())
        # print(f'{tick_price} and RSI {last_rsi}')
        
        # REAT TIME
        tickCounter +=1  
        napper +=1

        if barCount > 1:
        #SELL to close
            if STATE["live"] == 1 and STATE["long"] == 1:
                if tick_price > CANDLES[-1]["high_EMA"]:
                    if is_item_greater_or_less(CANDLES,"high","high_EMA",">",2):
                        SELL_MARKET()



                
                # if CANDLES[-1]['low_EMA'] > 0:
                #     if tick_price > CANDLES[-1]["high_EMA"]:
                #         if CANDLES[-2]["low_EMA"] > CANDLES[-2]["EMA1"]:
                #             if STATE["live"] == 1 and STATE["long"] == 1:
                #                 SELL_MARKET()

            #stop to close
            if STATE["live"] == 1 and STATE["long"] == 1:
                if tick_price < avg_trade_entry_price - STOP_LOSS*2.5:
                    if STATE["live"] == 1 and STATE["long"] == 1:
                        SELL_MARKET()
            
            # #SHORT
            if CANDLES[-1]["EMA1"] > 0:
                if tick_price > CANDLES[-1]["high_EMA"]:
                    #prev high
                    if CANDLES[-2]["low_EMA"] > CANDLES[-2]["EMA1"]:
                        if STATE["live"]==0 and STATE["short"]==0:
                            SHORT()

        


        # if STATE["live"] == 1 and STATE["long"] == 1:
        #     trail_stop(TRAIL_STOP_VALUE)
        #     if tick_price <= trail_stop_price:
        #         SELL_MARKET()
        #SELL TO CLOSES
        #TP

       


        # if STATE["live"] == 1 and STATE["long"] == 1:
            
        #     TRAIL_STOP_VALUE = diff_any_2_vals(CANDLES[-1]["high_EMA"],CANDLES[-1]["low_EMA"])
        #     print(f'CURRENT TRAIL_STOP_VALUE high ema - low ema: {TRAIL_STOP_VALUE}')

        #     trail_stop(TRAIL_STOP_VALUE)

        #     print(f'trail stop func: {trail_stop(TRAIL_STOP_VALUE)}')

        #     print(f'tick price {tick_price} vs trail stop price {trail_stop_price}')
            
            

            
             
        #     if tick_price >= avg_trade_entry_price + diff_any_2_vals(CANDLES[-1]["EMA1"],avg_trade_entry_price):
        #         STATE['trailing'] = 1
        #         print(f'trailing {STATE["trailing"]}')

        # if STATE["live"] == 1 and STATE["long"] == 1 and STATE['trailing'] ==1:
        #     trail_stop(TRAIL_STOP_VALUE)
            
            

        #     print(trail_stop_price)

            # print(f'tick_price: {tick_price} vs {trail_stop(diff_any_2_vals(avg_trade_entry_price-diff_any_2_vals(CANDLES[-1]["EMA1"],avg_trade_entry_price)))}')
            # if tick_price <= trail_stop_price:   
            #     SELL_MARKET()



        #TRAIL STOP
            # trail_stop(value)
            # if tick_price <= avg_trade_entry_price + (-2*diff_entry_to_EMA):
            #     SELL_MARKET()

            # print(f'RSI {last_rsi} tick: {tick_price} EMA1: {CANDLES[-1]["EMA1"]}   li Price: {avg_trade_entry_price} ')


        # REAT TIME End
        if is_candle_closed:
            barCount +=1
            
        #record Data!!!!
            if barCount > 1:
                CANDLES.append({"date": milsToDateTime(json_message['E']), "RSI":last_rsi, "close":float(candle['c']),"open":float(candle['o']),"high":float(candle['h']),"low":float(candle['l']),"volume":float(candle["v"]),"EMA1":0,"EMA2":0,"bar_length":0,"high_EMA":0,"low_EMA":0})
                closes.append(float(close))

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
                


                


            #record Data!!!!

                print(f'date: {CANDLES[-1]["date"]}  close: {CANDLES[-1]["close"]} high ema: {high_EMA}  EMA1: {CANDLES[-1]["EMA1"]} low ema: {low_EMA}' )
                
                
        #BUY RT
        if barCount > 1:
            

            # if CANDLES[-1]["EMA1"] > 0:
            #     #AI BUY
            #     if tick_price < CANDLES[-1]["EMA1"]: #below
            #         current_diff = CANDLES[-1]["EMA1"] - tick_price
            #         diff_EMA1_to_low_EMA = CANDLES[-1]["EMA1"] - CANDLES[-1]["low_EMA"]
            #         if current_diff >= diff_EMA1_to_low_EMA and diff_EMA1_to_low_EMA < 1:
            #             #PREVVVVVVVVVVVV BAR
            #             if CANDLES[-2]["close"] < CANDLES[-2]["EMA1"]: #below ema
            #                 prev_diff = CANDLES[-2]["EMA1"] - CANDLES[-2]["low"]
            #                 prev_diff_EMA1_to_low_EMA = CANDLES[-2]["EMA1"] - CANDLES[-2]["low_EMA"]
            #                 if prev_diff >= prev_diff_EMA1_to_low_EMA and prev_diff_EMA1_to_low_EMA < 1:
            #                     if STATE["live"]==0 and STATE["long"]==0:
            #                         BUY_MARKET()

            # if CANDLES[-1]["EMA1"] > 0:
                #current
                # if tick_below_x(-1,"EMA1"):
                #     if diff_candle_to_tick(-1,"EMA1") >= diff_a_to_b(-1,"EMA1",-1,"low_EMA"):
                #         # prev or -2
                #         if a_below_b(-2,"close",-2,'EMA1'):
                #             if diff_a_to_b(-2,"EMA1",-2,"low") > diff_a_to_b(-2,"EMA1",-2,"low_EMA"):
                #                 #prev or -3
                #                 if a_below_b(-3,"close",-3,'EMA1'):
                #                     if diff_a_to_b(-3,"EMA1",-3,"low") > diff_a_to_b(-3,"EMA1",-3,"low_EMA"):
                #                         #prev or -4
                #                         # if a_below_b(-4,"close",-4,'EMA1'):
                #                         #     if diff_a_to_b(-4,"EMA1",-4,"low") > diff_a_to_b(-4,"EMA1",-4,"low_EMA"):
                #                         if STATE["live"]==0 and STATE["long"]==0:
                #                             BUY_MARKET()
                
            #BUY MARKET 
            # if CANDLES[-1]["EMA1"] > 0:          
            #     if tick_price < CANDLES[-1]["low_EMA"]:
                    
            #         #prev high
            #         if CANDLES[-2]["high_EMA"] < CANDLES[-2]["EMA1"]:
            #             if STATE["live"]==0 and STATE["long"]==0:
            #                 BUY_MARKET()
            if CANDLES[-1]["EMA1"] > 0:
                if is_entry_cross_below(tick_price):
                    if STATE["live"]==0 and STATE["long"]==0:
                        BUY_MARKET()


                
            #TP SHORT CLOSE 
            if STATE["live"]==1 and STATE["short"]==1:
                if tick_price < CANDLES[-1]["low_EMA"]:
                    #prev bar
                    if CANDLES[-2]["high_EMA"] < CANDLES[-2]["EMA1"]:
                        if STATE["live"]==1 and STATE["short"]==1:
                            SHORT_CLOSE()
            #SL SHORT CLOSE
            if STATE["live"]==1 and STATE["short"]==1:
                if tick_price > avg_trade_entry_price + STOP_LOSS*2.5:
                    if STATE["live"]==1 and STATE["short"]==1:
                        print("short close STOP loss value is",STOP_LOSS)
                        SHORT_CLOSE()

            







            # if CANDLES[-1]["EMA1"] > 0:
            # #shortClose
            #     if STATE["live"]==1 and STATE["short"]==1:
            #         #tp
            #         if tick_price <= avg_trade_entry_price + (-1*(short_diff_value)):
            #             SHORT_CLOSE()
                    
            #         #stop
            #         if tick_price > avg_trade_entry_price + STOP_LOSS:
            #             SHORT_CLOSE()



                
                # if STATE["live"]==0 and STATE["short"]==0:
                #     if tick_price > CANDLES[-1]["EMA1"]: #above
                #         # redBar = CANDLES[i]["open"] > CANDLES[i]["close"] #redbar
                #         EMA_to_low_diff_short = tick_price - CANDLES[-1]["EMA1"]

                #         STRAT_DIFF = EMA_to_low_diff_short

                #         short_diff_value = CANDLES[-1]["EMA1"]-CANDLES[-1]["high_EMA"]

                #         print(F'short diff {short_diff_value}, short diff 667 {short_diff_value *.667}')
                        
                            
                #         if EMA_to_low_diff_short > short_diff_value*.667 and EMA_to_low_diff_short < 1:

                #             # print(CANDLES[i]["date"],"EMA TO LOW DIFF",EMA_to_low_diff)
                #             if STATE["live"]==0 and STATE["short"]==0:
                #                 SHORT()
        



                # if tick_price > CANDLES[-1]["EMA1"]:
                #     if CANDLES[-2]["close"] < CANDLES[-2]["EMA1"]:
                #         if CANDLES[-3]["close"] < CANDLES[-3]["EMA1"]:
                #                 BUY_MARKET()
            
        
        #strategy and signals
            #EMA CROSS in EMA8 3 Cross out
            # if barCount > 1:
            #     #buy to open
            #     if CANDLES[-1]["EMA3"] > CANDLES[-1]["EMA8"]:
            #         if CANDLES[-2]["EMA3"] < CANDLES[-2]["EMA8"]:
            #             if STATE["live"] == 0 and STATE["long"] ==0:
            #                 BUY_MARKET()
            #     #sell to close
            #     if CANDLES[-1]["close"] < CANDLES[-1]["EMA3"]:
            #         if CANDLES[-2]["close"] > CANDLES[-2]["EMA3"]:
            #             SELL_MARKET()
            
            #RSI EMA-5
            if barCount > 1:
                if len(closes) > RSI_PERIOD:
                    np_closes = numpy.array(closes)
                    rsi = talib.RSI(np_closes, RSI_PERIOD)
                    # print("All RSI's")
                    # print(rsi)
                    last_rsi = rsi[-1]
                    # print(f'the current rsi is {last_rsi}')
                
                #sell to close in bar
                        # if last_rsi > 70:
                        #     if STATE["live"] == 1 and STATE["long"] ==1:
                        #         SELL_MARKET()

                #sell to close in bar TAKE PROFIT
            

                

                
        # #buy to open in bar

        
        #REAL TIME BELOW
        #sell to close TRAIL STOP
        # if STATE["live"] == 1 and STATE["long"] ==1:
        #     trail_stop(TRAIL_STOP_VALUE)
        #     if tick_price <= trail_stop_price:
        #         SELL_MARKET()
            
        


        #test trade
        # if barCount > 1:
        #         if STATE["live"]==0:
        #             BUY_MARKET()
        
        # if STATE["live"] == 1 and STATE["long"] ==1:   
        #     print(avg_trade_entry_price,"Trail",trail_stop(TRAIL_STOP_VALUE))


        




        #debuging
        

        #DOJI
            # if barCount > 1:
            #     is_doji_previous_bar = doji(.20,.05,-2)


            # #EMAS
            #     is_bullish = close_above_2_Emas(CANDLES[-1]["EMA3"],CANDLES[-1]["EMA8"])

            # # #Bars
            #     is_tick_higher_then_prev_bar_high = tick_price > CANDLES[-2]["high"]

            #     #BUY DOJI STRATEGY
            #     if is_bullish:
            #         if is_doji_previous_bar:
            #             if is_tick_higher_then_prev_bar_high:
            #                 pass

            # if  STATE["live"] == 0:
            #     print("can buy")
            # if  STATE["live"] == 1:
            #     print("can sell")
    
        # open_below_2_Emas = history[-1].open_ < history[-1].EMATP and history[-1].open_ < history[-1].EMA70
        
            # if len(closes) > RSI_PERIOD:
            #     np_closes = numpy.array(closes)
            #     rsi = talib.RSI(np_closes, RSI_PERIOD)
            #     print("All RSI's")
            #     print(rsi)
            #     last_rsi = rsi[-1]
            #     print(f'the current rsi is {last_rsi}')

            #     if last_rsi > RSI_OVERBOUGHT:
            #         if in_position == True:
            #             print("SELLING>>>")
            #             order_succeeded = order(sym=TRADE_SYMBOL,side=SIDE_SELL,order_type=ORDER_TYPE_MARKET)
            #             if order_succeeded:
            #                in_position = False 
            #             #put binance logic to sell
            #         else:
            #             print("We don't own nothing yet")
                        

                    
            #     if last_rsi < RSI_OVERSOLD:
            #         if in_position:
            #             print(f'Its oversold but you already own')
            #             #binance logic to buy
            #         else:
            #             print("Buying..")
            #             order_succeeded = order(sym=TRADE_SYMBOL,side=SIDE_BUY,order_type=ORDER_TYPE_MARKET)
            #             if order_succeeded:
            #                 in_position = True

    except Exception as e:
        print("THERE IS AN ERROR",e)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)

ws.run_forever()
