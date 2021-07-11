import pyupbit

access = "H7Ig2CEVtccE2xr7YvfxWxMFeOgDkGfOtMxGT0qY"          # 본인 값으로 변경
secret = "gu8s8rcs1xLxNOte5H1KDEll1GYHyxHu3jRLdhvd"
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-BTC"))     # KRW-BTC 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회
