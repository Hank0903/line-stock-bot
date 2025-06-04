import datetime

def get_trading_days_between(start_date: str, end_date: str):
    """取得兩日期之間的所有交易日（排除週末）"""
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    days = []
    while start <= end:
        if start.weekday() < 5:  # 週一到週五
            days.append(start)
        start += datetime.timedelta(days=1)
    return days

def get_recent_trading_days(n=30, ref_date=None):
    """回推 n 天交易日，預設從今天"""
    today = ref_date or datetime.date.today()
    result = []
    delta = 0
    while len(result) < n:
        d = today - datetime.timedelta(days=delta)
        if d.weekday() < 5:
            result.append(d)
        delta += 1
    return list(reversed(result))


def date_to_query_format(date_obj):
    """將 datetime/date/str 轉為 YYYYMMDD（月初），供查詢用"""
    if isinstance(date_obj, str):
        date_obj = datetime.datetime.strptime(date_obj, "%Y-%m-%d")
    elif isinstance(date_obj, datetime.date) and not isinstance(date_obj, datetime.datetime):
        date_obj = datetime.datetime.combine(date_obj, datetime.time.min)
    return date_obj.strftime('%Y%m') + '01'
