import datetime

def get_recent_trading_days(n=30):
    today = datetime.date.today()
    result = []
    delta = 0
    while len(result) < n:
        d = today - datetime.timedelta(days=delta)
        if d.weekday() < 5:
            result.append(d.strftime('%Y%m%d'))
        delta += 1
    return list(reversed(result))

def date_to_query_format(date_str):
    # 將 '20250428' 轉換成 '20250401'（月初）
    return date_str[:6] + '01'
