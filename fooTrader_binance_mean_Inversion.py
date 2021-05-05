import websocket,json,pprint, talib, numpy

from binance.client import Client
from binance.enums import *
import config
import datetime
from helpers import *
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SOCKET = "wss://stream.binance.com:9443/ws/dogeusdt@kline_1m"
STATE = {"live":0,"long":0,"games":0,"set_A":0,"set_B":0,"set_C":0}
RSI_PERIOD =14
RSI_OVERBOUGHT =70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'DOGEUSDT'
TRADE_QUANTITY = 50
SELL_QUANTITY = 50
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
STOP_LOSS = 0.002

TAKE_PROFIT = .002
TRAIL_STOP_VALUE = .002

EMA1_WINDOW = 8
EMA2_WINDOW = 20

purchased_shares  = 0
tickCounter = 0
napper = 0

tick_open = 0
vers = 'panic2'

bar_Napper = 6

# subscribers = [{"name":"Foo","email":"3102796480@tmomail.net"},{"name":"fooGmail","email":"redfoo@partyrock.com"}]
foo ="3102796480@tmomail.net"
foomail = "redfoo@partyrock.com"
subscribers = [foo,foomail]


client = Client(config.API_KEY,config.API_SECRET, tld='us')

balance= client.get_asset_balance(asset='DOGE')
print(balance)


def email_Text(whom,sub,msg):
    
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    email = "redfoo@partyrock.com" # the email where you sent the email
    password = config.GMP
    send_to_email = str(whom) # for whom
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
    print("email server called")
    server.quit()

def send_mass_text(list,sub,msg):

    
    for sub in list:
        
        whom =sub
        
        email_Text(whom=whom,sub=sub,msg=msg)
    return


        

# def email_Text(sub,msg):
    
    
#         print(whom)

#         email = "redfoo@partyrock.com" # the email where you sent the email
#         password = config.GMP
#         send_to_email = "redfoo@partyrock" # for whom
#         subject = sub
#         message = msg

#         msg = MIMEMultipart()
#         msg["From"] = email
#         msg["To"] = send_to_email
#         msg["Subject"] = subject

#         msg.attach(MIMEText(message, 'plain'))

#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.starttls()
#         server.login(email, password)
#         text = msg.as_string()
#         server.sendmail(email, send_to_email, text)
#         print("email server called")
#         server.quit()
#         time.sleep(10)

# def mas_email(list):
#     for addy in list:

def trail_stop(value):
    global avg_trade_entry_price
    global trade_entry_prices
    global trade_ticks
    global trail_stop_price
    global tick_price
    global STOP_LOSS
    global trade_tick_high

    # print("inside Trail")
    
    
    if tick_price > avg_trade_entry_price:
        # print("passed condition")
    
        trade_ticks.append(tick_price)
        # print("appended")
        trade_tick_high = max(trade_ticks)
        # print()
        trail_stop_price = trade_tick_high - value
    

    

def BUY():
    order(sym=TRADE_SYMBOL,side=SIDE_BUY,order_type=ORDER_TYPE_MARKET,quan=TRADE_QUANTITY)
    return true

def BUY_MARKET():
    print("buy called")
    global STATE
    global trade_entry_prices
    global avg_trade_entry_price
    global purchased_shares
    global trail_stop_price
    global avg_trade_exit_price
    global napper
    global vers
    global STOP_LOSS
    global alex_email
    global foo_email
    global tick_price
    global bar_Napper
    global subscribers
    shares=[]

    if bar_Napper >= 0:

        if STATE["live"]==0 and STATE["long"]==0:
            #state
            napper = 0

            

            balance= client.get_asset_balance(asset="USDT")

                # set the percentage or fraction you want to invest in each order
            portion_balance = float(balance['free'])

            quan = (portion_balance / tick_price) * .05

            STATE["live"]=1
            STATE["long"]=1 

            order = client.order_market_buy(
            symbol=TRADE_SYMBOL,
            quantity=TRADE_QUANTITY)
            print(order)
            
            


            for obj in order["fills"]:
                
                trade_entry_prices.append(float(obj["price"]))
                # print(f'last trade entry price {trade_entry_prices[-1]}')
            # if len(trade_entry_prices) > 1:
            #     avg_trade_entry_price = sum(trade_entry_prices) / len(trade_entry_prices)
            # else:
            avg_trade_entry_price = trade_entry_prices[-1]

            trail_stop_price = avg_trade_entry_price - TRAIL_STOP_VALUE

            balance= client.get_asset_balance(asset="DOGE")

                # set the percentage or fraction you want to invest in each order
            portion_balance = float(balance['free'])

            send_mass_text(subscribers,f'ENTRY ', f' {avg_trade_entry_price}  {vers}') 
            

        
            print(f'ENTRY  {avg_trade_entry_price} @ {datetime.datetime.now()} Trail: {trail_stop_price} STATE: {STATE["live"]} , {STATE["long"]} ')

        

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
    global alex_email
    global foo_email
    global bar_Napper
    global subscribers
    if STATE["live"]==1 and STATE["long"]==1:
        if napper > 10:
            # You ask for the balance
            balance= client.get_asset_balance(asset="DOGE")

            # set the percentage or fraction you want to invest in each order
            portion_balance = float(balance['free']) * .5

            # you assign the created variable in the quantity of your order
            STATE["live"]=0
            STATE["long"]=0
            order = client.order_market_sell(
            symbol=TRADE_SYMBOL,
            quantity=SELL_QUANTITY)
            print(order)

            bar_Napper = 0
            
            

            for obj in order["fills"]:
                
                trade_entry_prices.append(float(obj["price"]))
                # print(f'last trade entry price {trade_entry_prices[-1]}')
            # if len(trade_entry_prices) > 1:
            #     avg_trade_exit_price = sum(trade_entry_prices) / len(trade_entry_prices)
            # else:
            avg_trade_exit_price = trade_entry_prices[-1]
            
            
            profit = avg_trade_exit_price - avg_trade_entry_price 
            send_mass_text(subscribers,f'Exit:{avg_trade_exit_price}', f'PROFIT:{profit} {vers} ')
            
            
            avg_trade_entry_price = 0
            trade_entry_prices = []
            trade_ticks = []
            trail_stop_price = 0
            
            print(f'EXIT  {CANDLES[-1]["close"]} @ {datetime.datetime.now()} STATE: {STATE["live"]} , {STATE["long"]} ')
            STATE["games"]+=1
            print("Sleeping")
            time.sleep(2)

        

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

#indicaters

def order(sym, side=SIDE_BUY,order_type=ORDER_TYPE_MARKET,quan=1):
    try:
        print("sending order...")
        order = client.create_test_order(symbol=sym, side=side, type=order_type, quantity=quan)
        print(order)
    except Exception as e:
        return False
    return True
 


def on_open(ws):
    print('open sesame')
    
    
    

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
        global tick_open
        global alex_email
        global foo_email
        global bar_Napper
        global subscribers


       

       

      

    
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

        # if STATE["live"] == 1 and STATE["long"] == 1:
        #     trail_stop(TRAIL_STOP_VALUE)
        #     if tick_price <= trail_stop_price:
        #         SELL_MARKET()
        #TP
        # if STATE["live"] == 1 and STATE["long"] == 1: 
        #         if tick_price >= avg_trade_entry_price + TAKE_PROFIT:
        #             SELL_MARKET()

            # print(f'RSI {last_rsi} tick: {tick_price} EMA1: {CANDLES[-1]["EMA1"]}   li Price: {avg_trade_entry_price} ')


        # REAT TIME End
        if is_candle_closed:
            print("Candle closed")
            barCount +=1
            bar_Napper +=1
            
        #record Data!!!!
            if barCount > 1:
                CANDLES.append({"date": milsToDateTime(json_message['E']), "RSI":last_rsi, "close":float(candle['c']),"open":float(candle['o']),"high":float(candle['h']),"low":float(candle['l']),"volume":float(candle["v"]),"EMA1":0,"EMA2":0})
                closes.append(float(close))
                #Indictors
                EMA1 = EMA("EMA1",closes,EMA1_WINDOW)
                
                if EMA1 > 0:
                    CANDLES[-1]["EMA1"] = EMA1
                
                EMA2 = EMA("EMA2",closes,EMA2_WINDOW)
                
                if EMA2 > 0:
                    CANDLES[-1]["EMA2"] = EMA2 
                print("before tick open")
                tick_open = tick_price
                print("after tick open")



              
            #record Data!!!!
                #panic for bars
                # if CANDLES[-1]["open"] > CANDLES[-1]["close"]: #red bar
                #     diff = CANDLES[-1]["open"] - CANDLES[-1]["close"]
                #     if abs(diff)  >= .015:
                #         print( f'Panic Bar {abs(diff)} position: {STATE["live"]}/{STATE["long"]})
                #         BUY_MARKET()
                
                #BUYYYY LOGIC
                if STATE["live"] == 0 and STATE["long"] ==0:
                    if CANDLES[-1]["open"] > CANDLES[-1]["close"]: #red bar
                        diff = CANDLES[-1]["open"] - CANDLES[-1]["close"]
                        if diff  >= .001:
                            print( f'Panic BAR {diff} position: {STATE["live"]}/{STATE["long"]}')
                            send_mass_text(subscribers,f'Panic BAR {diff}',f'position: {STATE["live"]}/{STATE["long"]}')
                            
                            BUY_MARKET()

                print(f'date: {CANDLES[-1]["date"]}  close: {CANDLES[-1]["close"]} EMA1: {EMA1} Entry Price: {avg_trade_entry_price} Trail: {trail_stop_price} Shares: {TRADE_QUANTITY}' )
                
                
           
                #panic bars BUYYYYYY 
                # if CANDLES[-1]["open"] > CANDLES[-1]["close"]: #red bar
                #     diff = CANDLES[-1]["open"] - CANDLES[-1]["close"]
                #     if abs(diff)  >= .015:
                #         print( f'Panic Bar {abs(diff)} position: {STATE["live"]}/{STATE["long"]})
                #         BUY_MARKET()


                
            # if CANDLES[-1]["close"] >= avg_trade_entry_price + TAKE_PROFIT:
            #     SELL_MARKET()

            #SELL LOGIC
            #TP
                if STATE["live"] == 1 and STATE["long"] ==1:
                    if CANDLES[-1]["close"] >= avg_trade_entry_price + TAKE_PROFIT:
                        
                        SELL_MARKET()
            #STOP LOSS
                if CANDLES[-1]["close"] <= avg_trade_entry_price - STOP_LOSS:
                    SELL_MARKET()
                
      
        if tickCounter % 1 == 0: 
            print(tick_open, 'vs', tick_price)
        
        




            




            
            #     if tick_price > CANDLES[-1]["EMA1"]:
            #         if CANDLES[-2]["close"] < CANDLES[-2]["EMA1"]:
            #             if CANDLES[-3]["close"] < CANDLES[-3]["EMA1"]:
            #                     BUY_MARKET()
            
        
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

            #     #sell to close in bar TAKE PROFIT
            

                

                
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
