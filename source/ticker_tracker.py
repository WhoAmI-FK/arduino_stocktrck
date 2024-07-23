import serial #To send to Arduino
import time #For Timers
import sys
from API import XTB
from threading import Timer
from XTBApi.api import Client

#(Notes for future distribution): Enter the serial port assigned to your Arduino here.
ser = serial.Serial('COM5', 9600, timeout=0.1)

#Global Variables
#Price Keys
fcurrent = "c"
fchange = "d"
fpchange = "dp"
curTrack = 0

orderId = -1
orderTrack = 0


MODELIST = ["BUY/OPEN","SELL/OPEN", "CLOSE/CLOSE"]

lastMode = "BUY/OPEN"
lastTrsCode = 0
doAct = False

allSymbols = []

def write(content):
    print("CONTENT: " + content)
    ser.write(content.encode())
    
def read(maxrange, maxorderl, curlot, steplot, maxlot, minlot):
        data = ser.readline().decode().strip()
        global curTrack
        global lastMode
        global doAct
        global orderTrack
        if data:
            list = data.split(" ")
            # for simplicity always increase cur track here
            for i in list:
                if i == "STOCK":
                        curTrack+=1
                        if curTrack == maxrange:
                            curTrack = 0
                if i == "ORDER":
                    if maxorderl > 0:
                        orderTrack += 1
                        print(orderTrack, " ", maxorderl)
                        if orderTrack == maxorderl:
                            orderTrack = 0
                if i in MODELIST:
                    lastMode = i
                if i == "ACT":
                   doAct = True
                if i == "INCLOT":
                    curlot += steplot
                    if curlot > maxlot:
                        curlot = maxlot
                if i == "DECLOT":
                    curlot -= steplot
                    if curlot < minlot:
                        curlot = minlot
                
            print("DATA: " + str(data))
        return curlot

def get_target():

    target_ticker = input("Welcome to the Ticker Tracker program.\nPlease enter your desired stock ticker symbol to begin (GOLD, BITCOIN...): ").upper()

    return target_ticker
    
def determine_indicators():

    #set indicator arrays
    available_indicators = [1, 2, 3, 4, 5]
    target_indicators = []
    choice = 0
    
    while choice != 5:

        print("Please select your desired indicators: (Note, certain indicators may require additional Arduino setup.")

        for indicator in available_indicators:

            if indicator == 1:
                print("1. Current Stock Price (###: XX.XX)")

            elif indicator == 2:
                print("2. Change Since Open (+X.XX)")

            elif indicator == 3:
                print("3. Percent Change Since Open (-X.XX%)")

            elif indicator == 4:
                print("4. Day Change Indicator Light (Green light or Red Light)")

            elif indicator == 5:
                print("5. Finish Program Setup")

        choice = int(input("Choice (1-5): "))

        if choice in available_indicators and choice != 5:

            available_indicators.remove(choice)
            target_indicators.append(choice)

        elif choice != 5:
            print("Not a valid selection.")
    
    #return chosen indicators
    return target_indicators

def get_price(candles):
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

def send_data(name, p, ind, balance, lmin, lmax, lstep):
    data = ""
    if 4 in ind:
        if float(p[fchange] >= 0):
            data += "M1:G;"
        else:
            data += "M1:R;"
    
    if 1 in ind:
        data += "M2:C;"
        time.sleep(.1)
        data += "M3:"+ f"{name}: {p[fcurrent]};"

    if 3 in ind:
        data += "M4:" + f"{p[fpchange]:.2f}%" + f" {p[fchange]};"
    
    data += "M5:" + "Account: " + "ACC_ID;"
    data += "M6:Balance: " + str(balance)+";"
    data += "M7:" + str(lmin) + ";"
    data += "M8:" + str(lmax) + ";"
    data += "M9:" + str(lstep) + ";"

def send_data2(name, p, ind, balance, lmin, lmax, lstep, curLot, margin, disOrderId):
    if 4 in ind:
        if float(p[fchange] >= 0):
            write("M1:G;")
        else:
            write("M1:R;")
    
    if 1 in ind:
        write("M2:C;")
        time.sleep(.1)
        write("M3:"+ f"{name}: {p[fcurrent]};")

    if 3 in ind:
        write("M4:" + f"{p[fpchange]:.2f}%" + f" {p[fchange]};")
    
    write("M5:" + "Account: " + "ACC_ID;")
    write("M6:Balance: " + str(balance)+";")
    write("M7:" + str(lmin) + ";")
    write("M8:" + str(lmax) + ";")
    write("M9:" + str(lstep) + ";")
    write("M10:" + str(curLot) + ";")
    write("M11:" + str(margin) + ";")
    write("M12:" + str(disOrderId) + ";")


def is_target_in_list(target, list, key='returnData', subkey='symbol'):
    for i in list[key]:
        if target == i[subkey]:
            return True
    return False

def get_open_trade_list_ids(list):
    return [trade_id for trade_id in list.keys()]

def get_open_trade_list(): # returns trade_ist
    client = Client()
    client.login("ACC_ID", "PASSWRD")
    trades = client.update_trades()
    client.logout()
    time.sleep(0.2)
    print(trades)
    return trades

def close_trade(trade_id):
    client = Client()
    client.login("ACC_ID", "PASSWRD")
    client.close_trade(trade_id)
    client.logout()
    time.sleep(0.2)    

def restart(is_full_rest):
    main(is_full_rest)

ticker = []
num = 0
indicators = []

def main(is_full_rest=True):
    
    #program setup
    global ticker
    if is_full_rest:
        ticker = []

    global num
    if is_full_rest:
        num = int(input("Input number of trackable tickers: "))
        i = 0
        while i < num:
            target = get_target()
            ticker.append(target)
            i+=1

    global indicators

    if is_full_rest:
        indicators = determine_indicators()
    API = XTB("ACC_ID", "PASSWRD")

    slist = API.get_AllSymbols()
    time.sleep(0.2)
    i = 0
    while i < num:
        if not is_target_in_list(ticker[i], slist):
            print("ERROR, TRACKER NOT IN THE LIST")
            restart(True) # restart application
        i+=1

    #loop
    interval_b = 5
    start_time_b = time.time()
    interval_API = 4
    start_time_API = time.time()
    global doAct
    global lastMode
    global orderTrack
    balance = API.get_Balance() 
    time.sleep(0.1)
    symboldata = API.get_Symbol(ticker[curTrack])
    curLot = symboldata['lotMin']
    minLot = symboldata['lotMin']
    maxLot = symboldata['lotMax']
    stepLot = symboldata['lotStep']
    olen = -1
    orderId = -1
    while 1==1:
        current_time_API = time.time()
        if current_time_API - start_time_API >= interval_API:
            orderlist = get_open_trade_list_ids(get_open_trade_list())
            olen = len(orderlist)
            if olen > 0:
                orderId = orderlist[orderTrack] 
            else:
                orderId = -1
            
            API.ping()
            time.sleep(0.1)
            candles = API.get_Candles("D1", ticker[curTrack], qty_candles=2)
            price = get_price(candles)

            current_time_b = time.time()
            if current_time_b - start_time_b >= interval_b:
             balance = API.get_Balance() 
             start_time_b = current_time_b

            margin = API.get_Margin(ticker[curTrack], curLot)
            time.sleep(0.2)
            send_data2(ticker[curTrack], price, indicators, balance, minLot, maxLot, stepLot, curLot, margin, orderId)
            start_time_API = current_time_API
        oldticker = ticker[curTrack]

        curLot = read(num, olen, curLot, stepLot, maxLot, minLot)
        if doAct == True:
            time.sleep(0.2)
            if lastMode == MODELIST[0]:
                status, order = API.make_Trade(ticker[curTrack], 0, 0, curLot)
                print(status)
                print(order)
                orderTrack = 0
            if lastMode == MODELIST[1]:
                status, order = API.make_Trade(ticker[curTrack], 1, 0, curLot)
                print(status)
                print(order)
                orderTrack = 0
            if lastMode == MODELIST[2]:
                if orderId != -1 and olen > 0:
                    close_trade(orderId)
                    orderTrack = 0
            doAct = False
        newticker = ticker[curTrack]
        if oldticker[curTrack] != newticker[curTrack]:
            symboldata = API.get_Symbol(ticker[curTrack])
            time.sleep(0.2)
            print(symboldata)
            curLot = symboldata['lotMin']
            minLot = symboldata['lotMin']
            maxLot = symboldata['lotMax']
            stepLot = symboldata['lotStep']

    API.logout()

#run program
if __name__ == "__main__":
    exceptionOccured = False
    while True:
        try:
            if not exceptionOccured:
                main(True)
            else:
                main(False)
                exceptionOccured = False
        except Exception as e:
            print(str(e))
            if isinstance(e, KeyboardInterrupt) or "ClearCommError" in str(e):
                sys.exit(0)
            else:
                print("ERROR OCCURED: ", e)
                exceptionOccured = True
        time.sleep(2)