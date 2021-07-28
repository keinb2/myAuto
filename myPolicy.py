import time
import pyupbit
import datetime
import numpy as np
import requests as rq
import header as my

access = my.access
secret = my.secret
myToken = my.myToken
myChannel = my.myChannel
start_str = my.start_str

g_interval = my.g_interval
limit_ratio = my.limit_ratio
coin = my.coin
targetCoin = my.targetCoin
krwUnit = my.krwUnit
tcoinUnit = my.tcoinUnit
gap_ratio = my.gap_ratio
position = my.position

def post_message(token, channel, text):
    response = rq.post("https://slack.com/api/chat.postMessage",
            headers={"Authorization": "Bearer "+token},
            data={"channel": channel, "text":text})

def get_start_time(ticker):
    #print("get_start_time called")
    df = pyupbit.get_ohlcv(ticker, interval=g_interval, count=1)
    return df.index[0]

def check_point(ticker, compare_ratio, ratio, charge, limit):
    #print("chek_point called")
    df = pyupbit.get_ohlcv(ticker, interval=g_interval, count=7)
    cur_close = df.iloc[6]['close']
    cur_open = df.iloc[6]['open']
    cur_high = df.iloc[6]['high']
    cur_low = df.iloc[6]['low']
    compare = cur_open*compare_ratio
    if charge == 1:
        if cur_close < cur_open :
            return -1
    elif cur_close < limit :
        return 2
    elif cur_close - cur_open > compare :
        if (cur_high - cur_close) > ((cur_high - cur_open)*ratio) :
            b_high = df.iloc[5]['high']
            bb_high = df.iloc[4]['high']
            bbb_high = df.iloc[3]['high']
            avg_high = 0
            for i in np.arange(0,6,1):
                avg_high += df.iloc[i]['high']
            avg_high /= 6
            if cur_close > avg_high and cur_close > b_high and cur_close > bb_high and cur_close > bbb_high :
                return 1
            else :
                return 0
        else :
            return 0
    elif cur_open - cur_close > compare :
        if (cur_close - cur_low) > ((cur_open - cur_low)*ratio) :
            b_low = df.iloc[5]['low']
            bb_low = df.iloc[4]['low']
            bbb_low = df.iloc[3]['low']
            avg_low = 0
            for i in np.arange(0,6,1):
                avg_low += df.iloc[i]['low']
            avg_low /= 6
            if cur_close<avg_low and cur_close<b_low and cur_close<bb_low and cur_close<bbb_low :
                return -1
            else :
                return 0
        else :
            return 0
    else :
        return 0

def get_balance(ticker):
    balances = upbit.get_balances()
    #print(balances)
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_limit(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['avg_buy_price'] is not None:
                return float(b['avg_buy_price'])*limit_ratio
            else:
                return 0
    return 0

upbit = pyupbit.Upbit(access, secret)
print(start_str)
post_message(myToken,myChannel,start_str)
skip = get_start_time("KRW-BTC")
skip_time = [skip] * len(coin)
before_status = [0] * len(coin)
try_purchase = [0] * len(coin)
need_charge = [0] * len(coin)
limit_price = [0] * len(coin)
while True:
    try:
        now = datetime.datetime.now()+datetime.timedelta(hours=9)
        start_time = get_start_time("KRW-BTC")
        for x in range(len(coin)):
            if skip_time[x] == start_time or skip_time[x] < start_time:
                skip_time[x] = start_time
                end_time = start_time + datetime.timedelta(minutes=10)
                if start_time < now and try_purchase[x] == 0 and now < (end_time - datetime.timedelta(seconds=7)):
                    point = check_point(coin[x],gap_ratio[x],position[x],need_charge[x],limit_price[x])
                    if point == -1 :
                        if before_status[x] == -1:
                            try_purchase[x] = -1
                        else :
                            krw = get_balance("KRW")
                            if krw > krwUnit[x]:
                                buy_result = upbit.buy_market_order(coin[x],krwUnit[x])
                                if need_charge[x] == 1 :
                                    need_charge[x] = 0
                                else :
                                    before_status[x] = -1
                                post_message(myToken,myChannel,"Target buy("+str(targetCoin[x])+") : " +str(buy_result))
                            else :
                                post_message(myToken,myChannel,"Not enough to buy "+str(targetCoin[x]))
                            limit_price[x] = get_limit(targetCoin[x])
                            skip_time[x] = end_time
                    elif point == 1 :
                        t_coin = get_balance(targetCoin[x])
                        if t_coin == 0:
                            if before_status[x] == 1:
                                need_charge[x] = 1
                        elif before_status[x] == 1:
                            try_purchase[x] = 1
                        else:
                            if t_coin > tcoinUnit[x]*1.5:
                                sell_result = upbit.sell_market_order(coin[x],tcoinUnit[x])
                            else :
                                sell_result = upbit.sell_market_order(coin[x],t_coin)
                            before_status[x] = 1
                            post_message(myToken,myChannel,"Target sell("+str(targetCoin[x])+") : " +str(sell_result))
                            limit_price[x] = get_limit(targetCoin[x])
                            skip_time[x] = end_time
                    elif point == 2 :
                        t_coin = get_balance(targetCoin[x])
                        before_status[x] = 2
                        sell_result = upbit.sell_market_order(coin[x],t_coin)
                        post_message(myToken,myChannel,"Target sell("+str(targetCoin[x])+") : " +str(sell_result))
                        limit_price[x] = 0
                        skip_time[x] = end_time
                elif try_purchase[x] != 0 and now > (end_time - datetime.timedelta(seconds=7)):
                    point = check_point(coin[x],gap_ratio[x]*1.5,position[x],need_charge[x],limit_price[x])
                    if point == -1:
                        krw = get_balance("KRW")
                        if krw > krwUnit[x]:
                            buy_result = upbit.buy_market_order(coin[x],krwUnit[x])
                            post_message(myToken,myChannel,"Target buy("+str(targetCoin[x])+") : " +str(buy_result))
                        else :
                            post_message(myToken,myChannel,"Not enough to buy "+str(targetCoin[x]))
                        before_status[x] = -1
                    elif point == 1 :
                        t_coin = get_balance(targetCoin[x])
                        if t_coin > tcoinUnit[x]*1.5:
                            sell_result = upbit.sell_market_order(coin[x],tcoinUnit[x])
                        else :
                            sell_result = upbit.sell_market_order(coin[x],t_coin)
                        before_status[x] = 1
                    else:
                        before_status[x] = 0
                    try_purchase[x] = 0
                    skip_time[x] = end_time
                else:
                    before_status[x] = 0
            time.sleep(1)

        #time.sleep(1)

    except Exception as e:
        print(e)
        post_message(myToken, myChannel, e)
        time.sleep(1)
