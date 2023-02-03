import time
from binance.client import Client
from datetime import  datetime
import datetime
from termcolor import colored
import os, time, config, requests
import defall
from binance.exceptions import BinanceAPIException
import os, requests, socket, urllib3


################################## API 등록 #######################################
with open("/Users/imbot/Desktop/code/futures/future_bot/api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    secret  = lines[1].strip()

client = Client(api_key, secret) #binance-python


##################################사용자 입력 창 #######################################
data_range = 5 ## 데이터 api 비교 간격
data_frequancy = 0.7 ## 데이터 api 호출 빈도_반응속도가 빨라짐
access_point = 0.25 ##진입 포인트 0.2~0.5 추천
escape_access_point = 0.4 #포지션 반대 변동성에 따른 탈출 
temp_price = [] ## 리스트 생성용 // 절대 건들지 말것
taker_fees    = 0.004
#####################################################################################

def DATAMAKER() :
    global temp_price
    global log_ret
    global escape_ret
    price = client.futures_symbol_ticker(symbol=pair)
    price_ls = float(price['price'])
    if len(temp_price) < data_range:
            temp_price.append(price_ls)
            temp_price = temp_price[0:]
    elif len(temp_price) == data_range:  
        del temp_price[0]  
        if len(temp_price) >= (data_range-1) :
            log_ret = ((temp_price[-1]) - (temp_price[-(data_range-1)]))/(temp_price[-(data_range-1)])*100
            escape_ret = ((temp_price[-1]) - (temp_price[-(data_range-1)]))/(temp_price[-(data_range-1)])*100
            print('모니터링 action 계수 : ', log_ret)
    print(temp_price)

def MONITOR():

    global log_ret
    if len(temp_price) >= (data_range-1) :
        log_ret = ((temp_price[-1]) - (temp_price[-(data_range-1)]))/(temp_price[-(data_range-1)])*100
        #short_data = log_ret - access_point
        #long_data = log_ret - access_point
        if log_ret < -(access_point) :
            print(colored("숏 진입 특이점에 도달했습니다","red"),log_ret,'%')
            return "SHORT"
        elif log_ret > access_point :
        #and SHORT_SIDE == "NO POSITION":
            print(colored("롱 진입 특이점에 도달했습니다","green"),log_ret,'%')
            return "LONG"
        
            #market_open_short()
            #숏 포지션 오픈 및 숏 클로즈 조건 설정
def ESCAPE():
    global escape_ret
    if len(temp_price) >= (data_range-1) :
        escape_ret = ((temp_price[-1]) - (temp_price[-(data_range-1)]))/(temp_price[-(data_range-1)])*100
        #short_data = log_ret - access_point
        #long_data = log_ret - access_point
        if escape_ret < -(escape_access_point) :
            print(colored("롱, 긴급탈출~!!!!","red"),escape_ret,'%')
            return "SHORT"
        elif escape_ret > escape_access_point :
        #and SHORT_SIDE == "NO POSITION":
            print(colored("숏, 긴급탈출~!!!!","green"),escape_ret,'%')
            return "LONG"        
    
def start(pair,leverage, quantity) :
    print("프로그램을 정상운영 중")
    print(pair)
    response = defall.position_information(pair)
    if response[0].get('marginType') != "isolated": 
        defall.change_margin_to_ISOLATED(pair)
    
    if response[0].get('leverage') != leverage :
        defall.change_leverage(pair, leverage)
        
    if defall.LONG_SIDE(response) == "NO_POSITION" :
        if MONITOR() == "LONG" and float(response[1].get('positionAmt')) == 0 and float(response[2].get('positionAmt')) == 0:
            defall.market_open_long(pair, quantity)
        else:
            print(colored("롱 포지션 : 모니터링 코드 작동 중", "green"))
   
    if defall.LONG_SIDE(response) == "LONGING" :
        if float(response[1].get('entryPrice'))*1.0027 < (temp_price[-1]) or ESCAPE() == "SHORT":
            defall.market_close_long(pair, quantity)
            print("익절 코드 작동 "+str(float(response[1].get('entryPrice')))+" | 현재가격: "+str(float(response[1].get('markPrice')))+" | positionAmt: "+str(float(response[1].get('positionAmt')))+" | unRealizedProfit "+str(float(response[1].get('unRealizedProfit')))+"| InProfit "+str(in_Profit_show(response[1])))
        elif float(response[1].get('entryPrice'))*0.98 > (temp_price[-1]) :
            defall.market_close_long(pair, quantity)
            print("1% 손실, 손절코드 작동")
            
        else : 
            print(colored("롱 포지션 : 롱 포지션 유지 중","green"))
            print("진입가격 : "+str(float(response[1].get('entryPrice')))+" | 현재가격: "+str(float(response[1].get('markPrice')))+" | positionAmt: "+str(float(response[1].get('positionAmt')))+" | unRealizedProfit "+str(float(response[1].get('unRealizedProfit')))+"| InProfit "+str(in_Profit_show(response[1])))
    
    if defall.SHORT_SIDE(response) == "NO_POSITION" :
        if MONITOR() == "SHORT" and float(response[1].get('positionAmt')) == 0 and float(response[2].get('positionAmt')) == 0:
            defall.market_open_short(pair, quantity)
        else:
            print(colored("숏 포지션 : 모니터링 코드 작동 중","red"))
            
    if defall.SHORT_SIDE(response) == "SHORTING" :
        if float(response[2].get('entryPrice'))*0.997 > (temp_price[-1]) or ESCAPE() == "LONG":
            defall.market_close_short(pair, quantity)
            print("익절 코드 작동"+str(float(response[2].get('entryPrice')))+" | 현재가격: "+str(float(response[2].get('markPrice')))+" | positionAmt: "+str(float(response[2].get('positionAmt')))+" | unRealizedProfit "+str(float(response[2].get('unRealizedProfit')))+"| InProfit "+str(in_Profit_show(response[2])))
        elif float(response[2].get('entryPrice'))*1.02 < (temp_price[-1]) :
            defall.market_close_short(pair, quantity)
            print("1% 손실, 손절 코드 작동 "+str(float(response[2].get('entryPrice')))+" | 현재가격: "+str(float(response[2].get('markPrice')))+" | positionAmt: "+str(float(response[2].get('positionAmt')))+" | unRealizedProfit "+str(float(response[2].get('unRealizedProfit')))+"| InProfit "+str(in_Profit_show(response[2])))
        else :
             print(colored("숏 포지션 : 숏 포지션 유지 중", "red"))
             print("진입가격 : "+str(float(response[2].get('entryPrice')))+" | 현재가격: "+str(float(response[2].get('markPrice')))+" | positionAmt: "+str(float(response[2].get('positionAmt')))+" | unRealizedProfit "+str(float(response[2].get('unRealizedProfit')))+"| InProfit "+str(in_Profit_show(response[2])))   
    
    
def in_Profit(response):
    # taker_fees    = 0.2 changed to 0.3 to triedls
    global taker_fees
    markPrice     = float(response.get('markPrice'))
    positionAmt   = abs(float(response.get('positionAmt')))
    unRealizedPNL = round(float(response.get('unRealizedProfit')), 2)
    breakeven_PNL = (markPrice * positionAmt * taker_fees) / 100
    return True if unRealizedPNL > breakeven_PNL else False

def in_Profit_show(response):
    # taker_fees    = 0.2 changed to 0.3 to tried
    #taker_fees    = 0.2
    global taker_fees
    markPrice     = float(response.get('markPrice'))
    positionAmt   = abs(float(response.get('positionAmt')))
    unRealizedPNL = round(float(response.get('unRealizedProfit')), 2)
    breakeven_PNL = (markPrice * positionAmt * taker_fees) / 100
    return round(breakeven_PNL,(data_range-1))    


try:
    while True:
        try:
            pair     = config.pair
            leverage = config.leverage
            quantity = config.quantity
            DATAMAKER()
            start(pair, leverage, quantity)
            time.sleep(data_frequancy) #sleep to avoid penality

        except (socket.timeout,
                BinanceAPIException,
                urllib3.exceptions.ProtocolError,
                urllib3.exceptions.ReadTimeoutError,
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
                ConnectionResetError, KeyError, OSError) as e:

            if not os.path.exists("ERROR"): os.makedirs("ERROR")
            with open((os.path.join("ERROR", config.pair + ".txt")), "a", encoding="utf-8") as error_message:
                error_message.write("[!] " + config.pair + " - " + "Created at : " + "\n" + str(e) + "\n\n")
                print(e)
                

except KeyboardInterrupt: print("\n\nAborted.\n")