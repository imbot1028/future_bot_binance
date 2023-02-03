from binance.client import Client
import pprint
from termcolor import colored

with open("./api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    secret  = lines[1].strip()

client = Client(api_key, secret) #binance-python
ticker = 'NKNUSDT'

response = client.futures_position_information(symbol = ticker)
print(colored('response 0 : ','green') ,response[0])
print(colored('response 1 : ', 'red') ,response[1])
print(colored('response 2 : ', 'yellow') ,response[2])
