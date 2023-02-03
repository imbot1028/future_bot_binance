import ccxt

live_trade = False

quantity = 100
leverage = 10
pair = 'LUNA2USDT'

trade_balance =  60 #조정
pair_price = 4.5 #조정

quantity_result = trade_balance*leverage/pair_price

print("Pair Name        :   " , pair)
print("Trade Quantity   :   " , quantity)
print("Leverage         :   " , leverage)
print('quantity : ', quantity_result)
