import time
import pyupbit
import datetime
import numpy as np
import requests as rq

access = "H7Ig2CEVtccE2xr7YvfxWxMFeOgDkGfOtMxGT0qY"
secret = "gu8s8rcs1xLxNOte5H1KDEll1GYHyxHu3jRLdhvd"
#myToken = "xoxb-2236073360373-2262793371296-cMOjFVIzRCLc0trl6UDhtSjR"
#myChannel = "#crypto"
start_str = "Start XRP HUNT MLK autoTrade"

g_interval = 'minute10'
coin = ("KRW-XRP", "KRW-HUNT", "KRW-MLK")
targetCoin = ("XRP", "HUNT", "MLK")
krwUnit = (20000, 20000, 20000)
tcoinUnit = (28, 66, 18)
gap_ratio = (0.007, 0.007, 0.007)
position = (0.27, 0.27, 0.27)

#def post_message(token, channel, text):
#    response = rq.post("https://slack.com/api/chat.postMessage",
#            headers={"Authorization": "Bearer "+token},
#            data={"channel": channel, "text":text})

def get_start_time(ticker):
    #print("get_start_time called")
    df = pyupbit.get_ohlcv(ticker, interval=g_interval, count=1)
    return df.index[0]

def check_point(ticker, compare_ratio, ratio):
    #print("chek_point called")
    df = pyupbit.get_ohlcv(ticker, interval=g_interval, count=7)
    #print(df.iloc[6])
    cur_close = df.iloc[6]['close']
    cur_open = df.iloc[6]['open']
    cur_high = df.iloc[6]['high']
    cur_low = df.iloc[6]['low']
    compare = cur_open*compare_ratio
    #print("cur_close : ",cur_close)
    #print("cur_open : ",cur_open)
    #print("cur_high : ",cur_high)
    #print("cur_low : ",cur_low)
    if cur_close - cur_open > compare :
        if (cur_high - cur_close) > ((cur_high - cur_open)*ratio) :
            b_high = df.iloc[5]['high']
            bb_high = df.iloc[4]['high']
            bbb_high = df.iloc[3]['high']
            avg_high = 0
            for i in np.arange(0,6,1):
                avg_high += df.iloc[i]['high']
            #print("high sum : ",avg_high)
            avg_high /= 6
            #print("avg_high : ",avg_high)
            #print("b_high : ",b_high)
            #print("bb_high : ",bb_high)
            #print("bbb_high : ",bbb_high)
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
            #print("low sum : ",avg_low)
            avg_low /= 6
            #print("avg_low : ",avg_low)
            #print("b_low : ",b_low)
            #print("bb_low : ",bb_low)
            #print("bbb_low : ",bbb_low)
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

upbit = pyupbit.Upbit(access, secret)
print(start_str)
#post_message(myToken,myChannel,start_str)
skip = get_start_time("KRW-BTC")
skip_time = [skip] * len(coin)
while True:
    try:
        now = datetime.datetime.now()+datetime.timedelta(hours=9)
        start_time = get_start_time("KRW-BTC")
        for x in range(len(coin)):
            if skip_time[x] == start_time or skip_time[x] < start_time:
                skip_time[x] = start_time
                end_time = start_time + datetime.timedelta(minutes=10)
                if start_time < now and now < (end_time - datetime.timedelta(seconds=7)):
                    point = check_point(coin[x],gap_ratio[x],position[x])
                    #print(point)
                    if point == -1 :
                        krw = get_balance("KRW")
                        if krw > krwUnit[x]:
                            buy_result = upbit.buy_market_order(coin[x],krwUnit[x])
                            #post_message(myToken,myChannel,"Target buy : " +str(buy_result))
                        #else :
                            #print("Try to buy but no KRW")
                            #post_message(myToken,myChannel,"Not enough to buy "+coin[x])
                        skip_time[x] = end_time
                    elif point == 1 :
                        t_coin = get_balance(targetCoin[x])
                        if t_coin > tcoinUnit[x]:
                            sell_result = upbit.sell_market_order(coin[x],tcoinUnit[x])
                        else :
                            sell_result = upbit.sell_market_order(coin[x],t_coin)
                        #post_message(myToken,myChannel,"Target sell : " +str(sell_result))
                        skip_time[x] = end_time
            time.sleep(1)

        #time.sleep(1)

    except Exception as e:
        print(e)
        #post_message(myToken, myChannel, e)
        time.sleep(1)
