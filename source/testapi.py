from API import XTB
import finnhub
from XTBApi.api import Client


API = XTB("ACC_ID", "PASSWRD")

#balance = API.get_Balance()
#print(balance)

info = API.get_Symbol("ETHEREUM")
fhub = finnhub.Client(api_key="API")


#result = API.make_Trade("STELLAR", 0, 0, 1000, comment="comment")

lotMin = info['lotMin']
lotMax = info['lotMax']
lotStep = info['lotStep']
candles = API.get_Candles("D1", "ETHEREUM", qty_candles=2)
def getPrice(candles):
    for i in range(1,len(candles)):
        candles[i]['open'] /= (10**candles[0]['digits'])
        candles[i]['close'] /= (10**candles[0]['digits'])
        candles[i]['close']+=candles[i]['open']
        candles[i]['high'] /= (10**candles[0]['digits'])
        candles[i]['high'] += candles[i]['open']
        candles[i]['low'] /= (10**candles[0]['digits'])
        candles[i]['low'] += candles[i]['open']

    formatedCandles = {
        'c': round(candles[(len(candles)-1)]['close'],2),
        'd': round(candles[(len(candles)-1)]['close'] - candles[(len(candles)-2)]['close'],2),
        'dp': round((candles[(len(candles)-1)]['close'] - candles[(len(candles)-2)]['close'])/candles[(len(candles)-2)]['close'],2)
    }

    return formatedCandles



margin = API.get_Margin("ETHEREUM", 0.05)

print("MARGIN:")
print(margin)
print(candles)
print(getPrice(candles=candles))
print(lotMin)

print(info)

print(fhub.quote("SPY"))

print("RESULT")


client = Client()

client.login("ACC_ID", "PASSWRD")

client.check_if_market_open(["ETHEREUM"])

client.open_trade('buy', "ETHEREUM", 0.05)

trades = client.update_trades()
for trade in trades:
    actual_profit = client.get_trade_profit(trade) # CHECK PROFIT
    if actual_profit >= 100:
        client.close_trade(trade) # CLOSE TRADE
# CLOSE ALL OPEN TRADES
client.close_all_trades()
# THEN LOGOUT
client.logout()
API.logout()