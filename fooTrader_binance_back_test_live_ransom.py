import websocket,json,pprint, talib, numpy

from binance.client import Client
from binance.enums import *
import config
import datetime
from helpers import *
import time

SOCKET = "wss://stream.binance.com:9443/ws/dogeusdt@kline_1m"
STATE = {"live":0,"long":0,"games":0,"set_A":0,"set_B":0,"set_C":0,"simulation":1}
RSI_PERIOD =14
RSI_OVERBOUGHT =70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'DOGEUSDT'
TRADE_QUANTITY = 3500
SELL_QUANTITY = 3500
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
STOP_LOSS = 0

TAKE_PROFIT = .007
TRAIL_STOP_VALUE = .005

EMA1_WINDOW = 8
EMA2_WINDOW = 20

purchased_shares  = 0
tickCounter = 0
napper = 0
vers = 'mean rev'
i=0
running_profit = 0
shares =10000




client = Client(config.API_KEY,config.API_SECRET, tld='us')



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
    shares=[]


    if STATE["simulation"]==1:
        if STATE["live"]==0 and STATE["long"]==0:
            STATE["live"]=1
            STATE["long"]=1
            avg_trade_entry_price = CANDLES[i]["close"]

            print(f'{CANDLES[i]["date"]} BUYYYYYYYYY Entrty Price: {avg_trade_entry_price}')


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

            trail_stop_price = avg_trade_entry_price - TRAIL_STOP_VALUE
            print(f'ENTRY  {avg_trade_entry_price} @ {datetime.datetime.now()} Trail: {trail_stop_price} STATE: {STATE["live"]} , {STATE["long"]} ')

            email_Text(f'ENTRY {avg_trade_entry_price}', f' Trail: {trail_stop_price} {vers}')
            
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

    if STATE["simulation"]==1:
        if STATE["live"]==1 and STATE["long"]==1:
            
            STATE["live"]=0
            STATE["long"]=0

            avg_trade_exit_price = CANDLES[i]["close"]
            profit = avg_trade_exit_price - avg_trade_entry_price
            running_profit += profit
            print(f'{CANDLES[i]["date"]} SELLLLLLL EXIT: {avg_trade_exit_price} Profit = {profit}') 
            

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
                
                
                email_Text(f'Exit:{avg_trade_exit_price}', f'PROFIT:{profit} {vers} ')
                
                avg_trade_entry_price = 0
                trade_entry_prices = []
                trade_ticks = []
                trail_stop_price = 0
                STATE["live"]=0
                STATE["long"]=0
                STATE["games"]+=1
                print("Sleeping")
                time.sleep(2)
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
 




###################################### GET HISTORY BARS
if STATE["simulation"]==1:
    historical_bars = client.get_historical_klines("DOGEUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    # historical_bars = client.get_historical_klines("DOGEUSDT", Client.KLINE_INTERVAL_1MINUTE, "21 Apr, 2021", "")


   

    hist_bars = []
    length_list = []
    for bar in historical_bars:
        CANDLES.append({"date": milsToDateTime(bar[0]), "close":float(bar[4]),"open":float(bar[1]),"high":float(bar[2]),"low":float(bar[3]),"volume":float(bar[5]),"RSI":0,"EMA1":0,"EMA2":0,"bar_length":0})
        closes.append(float(bar[4]))
        #Indictors
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
        if EMA1 > 0:

            print(f'DATE: {CANDLES[i]["date"]} CLOSE: {CANDLES[i]["close"]} EMA1 {CANDLES[i]["EMA1"]}')
            
            if CANDLES[i]["close"] < CANDLES[i]["EMA1"]: #below
                redBar = CANDLES[i]["open"] > CANDLES[i]["close"] #redbar
                EMA_to_low_diff = CANDLES[i]["EMA1"] - CANDLES[i]["low"]
                if redBar:
                    
                    if EMA_to_low_diff > .002 and EMA_to_low_diff < 1:

                        # print(CANDLES[i]["date"],"EMA TO LOW DIFF",EMA_to_low_diff)
                        if STATE["live"]==0 and STATE["long"]==0:
                            BUY_MARKET()
                        # profit = CANDLES[i+EMA1_WINDOW]["close"] - CANDLES[i+EMA1_WINDOW-1]["low"]
                        # if profit > .05:
                        #     print(CANDLES[i+EMA1_WINDOW]["date"],f'profit {profit}')
        # Sell
            if STATE["live"]==1 and STATE["long"]==1:
                
                if CANDLES[i]["close"] > avg_trade_entry_price + .007:
                    SELL_MARKET()
        
    print(f'running prof:{running_profit * 30000}')

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

        #SELL
        # if STATE["live"] == 1 and STATE["long"] == 1:
        #     trail_stop(TRAIL_STOP_VALUE)
        #     if tick_price <= trail_stop_price:
        #         SELL_MARKET()
        #TP
        if STATE["live"] == 1 and STATE["long"] == 1: 
                if tick_price >= avg_trade_entry_price + TAKE_PROFIT:
                    SELL_MARKET()

            # print(f'RSI {last_rsi} tick: {tick_price} EMA1: {CANDLES[-1]["EMA1"]}   li Price: {avg_trade_entry_price} ')


        # REAT TIME End
        if is_candle_closed:
            barCount +=1
            
        #record Data!!!!
            if barCount > 1:
                CANDLES.append({"date": milsToDateTime(json_message['E']), "RSI":last_rsi, "close":float(candle['c']),"open":float(candle['o']),"high":float(candle['h']),"low":float(candle['l']),"volume":float(candle["v"]),"EMA1":0,"EMA2":0,"bar_length":0})
                closes.append(float(close))
                #Indictors
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

                # print(f'date: {CANDLES[-1]["date"]}  close: {CANDLES[-1]["close"]} EMA1: {EMA1} Entry Price: {avg_trade_entry_price} Trail: {trail_stop_price} Shares: {TRADE_QUANTITY}' )
                
        #BUY RT
        if barCount > 1:

            if CANDLES[-1]["EMA1"] > 0:
                if tick_price < CANDLES[-1]["EMA1"]: #below
                    # redBar = CANDLES[-1]["open"] > CANDLES[-1]["close"] #redbar
                    EMA_to_low_diff = CANDLES[-1]["EMA1"] - tick_price
                    
                        
                    if EMA_to_low_diff > .005 and EMA_to_low_diff < 1:

                        # print(CANDLES[i]["date"],"EMA TO LOW DIFF",EMA_to_low_diff)
                        if STATE["live"]==0 and STATE["long"]==0:
                            BUY_MARKET()


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
