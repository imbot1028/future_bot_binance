from statistics import quantiles
import time
from binance.client import Client
from termcolor import colored
#api_key
with open("./api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    secret  = lines[1].strip()
client = Client(api_key, secret) #binance-python

def get_timestamp():
    return int(time.time() * 1000)

def position_information(pair):
    return client.futures_position_information(symbol=pair)

def account_trades(pair, timestamp) :
    return client.futures_account_trades(symbol=pair, timestamp=get_timestamp(), startTime=timestamp)

def LONG_SIDE(response):
    if float(response[1].get('positionAmt')) > 0: 
        return "LONGING"
    elif float(response[1].get('positionAmt')) == 0: 
        return "NO_POSITION"

def SHORT_SIDE(response):
    if float(response[2].get('positionAmt')) < 0 : 
        return "SHORTING"
    elif float(response[2].get('positionAmt')) == 0: 
        return "NO_POSITION"
    
def change_leverage(pair, leverage):
    return client.futures_change_leverage(symbol=pair, leverage=leverage, timestamp=get_timestamp())

def change_margin_to_ISOLATED(pair):
    return client.futures_change_margin_type(symbol=pair, marginType="ISOLATED", timestamp=get_timestamp())

def set_hedge_mode(): 
    if not client.futures_get_position_mode(timestamp=get_timestamp()).get('dualSidePosition'):
        return client.futures_change_position_mode(dualSidePosition="true", timestamp=get_timestamp())

def market_open_long(pair, quantity):
    client.futures_create_order(symbol=pair,
                                quantity=quantity,
                                positionSide="LONG",
                                type="MARKET",
                                side="BUY",
                                timestamp=get_timestamp())
    print(colored("롱포지션 진입", "green"))

def market_open_short(pair, quantity):
    client.futures_create_order(symbol=pair,
                                quantity=quantity,
                                positionSide="SHORT",
                                type="MARKET",
                                side="SELL",
                                timestamp=get_timestamp())
    print(colored("숏포지션 진입", "red"))



def market_close_long(pair, quantity):
    client.futures_create_order(symbol=pair,
                                quantity = quantity,
                                positionSide="LONG",
                                side="SELL",
                                type="MARKET",
                                timestamp=get_timestamp())
    print("롱포지션 종료")


def market_close_short(pair, quantity):
    client.futures_create_order(symbol=pair,
                                quantity= quantity,
                                positionSide="SHORT",
                                side="BUY",
                                type="MARKET",
                                timestamp=get_timestamp())
    print("숏포지션 종료")

