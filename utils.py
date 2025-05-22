import datetime

def get_recent_trading_days(n=30):
    """取得最近 n 個交易日（不含假日）"""
    today = datetime.date.today()
    result = []
    delta = 0
    while len(result) < n:
        d = today - datetime.timedelta(days=delta)
        if d.weekday() < 5:
            result.append(d)
        delta += 1
    return list(reversed(result))

def date_to_query_format(date_input):
    """將日期轉換為 YYYYMM01 格式（當月第一天）"""
    if isinstance(date_input, str):
        date_input = datetime.datetime.strptime(date_input, '%Y%m%d')
    return date_input.strftime('%Y%m') + '01'
