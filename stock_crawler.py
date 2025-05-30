import re
import requests
import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import mplfinance as mpf
from utils import get_recent_trading_days, date_to_query_format

# 圖片設定
IMAGE_OUTPUT_FOLDER = 'static'
IMAGE_HOST_URL = 'https://line-stock-bot-iwcn.onrender.com/static'
os.makedirs(IMAGE_OUTPUT_FOLDER, exist_ok=True)

# 中文字體設定
font_path = 'static/fonts/NotoSansTC-Regular.ttf'
prop = fm.FontProperties(fname=font_path)

# 🧠 日期工具
def get_trading_days_between(start_date: str, end_date: str) -> list[datetime.datetime]:
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    days = []
    while start <= end:
        if start.weekday() < 5:  # 排除週末
            days.append(start)
        start += datetime.timedelta(days=1)
    return days

# ✅ 取得股票資料（指定天數）
def get_stock_data(stock_no: str, days: int = 30):
    dates = get_recent_trading_days(days)
    return fetch_stock_data(stock_no, dates, max_days=days)

# ✅ 取得股票資料（指定日期區間）
def get_stock_data_by_date(stock_no: str, start: str, end: str):
    dates = get_trading_days_between(start, end)
    return fetch_stock_data(stock_no, dates)

def fetch_stock_data(stock_no: str, dates, max_days=None):
    # 確保 dates 是 datetime 物件列表
    def ensure_datetime(d):
        if isinstance(d, datetime.datetime):
            return d
        elif isinstance(d, datetime.date):
            return datetime.datetime.combine(d, datetime.time.min)
        elif isinstance(d, str):
            # 試著解析格式為 YYYYMMDD
            return datetime.datetime.strptime(d, "%Y%m%d")
        else:
            raise ValueError(f"不支援的日期格式：{type(d)}")

    dates = [ensure_datetime(d) for d in dates]
    target_dates_set = set(d.date() for d in dates)


    # 取得需要抓取的月份字串（例如 '202405'）
    months_to_fetch = sorted(set(d.strftime('%Y%m') for d in dates))
    data = []

    for month_key in months_to_fetch:
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={month_key}01&stockNo={stock_no}"
        try:
            r = requests.get(url, verify=False, timeout=10)
            json_data = r.json()
            if json_data['stat'] != 'OK':
                continue
            for row in json_data['data']:
                # 民國年轉西元年
                roc_date = row[0]
                parts = roc_date.split('/')
                if len(parts[0]) == 3:
                    parts[0] = str(int(parts[0]) + 1911)
                date_fmt = '-'.join(parts)
                parsed_date = datetime.datetime.strptime(date_fmt, '%Y-%m-%d')
                if parsed_date.date() not in target_dates_set:
                    continue
                data.append({
                    "日期": parsed_date,
                    "開盤價": float(row[3].replace(',', '')),
                    "最高價": float(row[4].replace(',', '')),
                    "最低價": float(row[5].replace(',', '')),
                    "收盤價": float(row[6].replace(',', '')),
                    "成交量": float(row[1].replace(',', '')),
                })
        except Exception as e:
            print(f"❌ 錯誤：{e}")
            continue

    df = pd.DataFrame(data)
    df = df.sort_values("日期")

    if max_days is not None:
        df = df.tail(max_days)

    return df


# ✅ 產生 K 線圖（依天數）
def generate_kline_image(stock_no: str, days: int = 30, show_sma=False):
    df = get_stock_data(stock_no, days)
    if df.empty:
        raise Exception("❌ 無法取得資料")
    filename = f"{stock_no}_kline.jpg"
    filepath = os.path.join(IMAGE_OUTPUT_FOLDER, filename)
    plot_kline(df, stock_no, filepath, show_sma)
    return filename

# ✅ 產生 K 線圖（依日期區間）
def generate_kline_image_by_date(stock_no: str, start: str, end: str, show_sma=False):
    df = get_stock_data_by_date(stock_no, start, end)
    if df.empty:
        raise Exception("❌ 無法取得資料")
    filename = f"{stock_no}_{start}_to_{end}.jpg"
    filepath = os.path.join(IMAGE_OUTPUT_FOLDER, filename)
    plot_kline(df, stock_no, filepath, show_sma)
    return filename

# ✅ 繪圖邏輯
def plot_kline(df: pd.DataFrame, stock_no: str, filepath: str, show_sma=False):
    df = df.copy()
    df.set_index('日期', inplace=True)
    df.rename(columns={
        '開盤價': 'Open',
        '最高價': 'High',
        '最低價': 'Low',
        '收盤價': 'Close',
        '成交量': 'Volume'
    }, inplace=True)

    mc = mpf.make_marketcolors(up='red', down='green', edge='inherit', wick='inherit', volume='inherit')
    s = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=mc)

    mpf.plot(
        df,
        type='candle',
        mav=(10, 30) if show_sma else (),
        volume=True,
        title=f"{stock_no} K line ({len(df)} days)",
        style=s,
        savefig=dict(fname=filepath, dpi=100, bbox_inches='tight'),
        datetime_format='%b %d',
        xrotation=15,
        tight_layout=True
    )

# ✅ 股價資訊簡訊
def get_stock_info(stock_no: str):
    url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=20240401&stockNo={stock_no}"
    try:
        r = requests.get(url, verify=False, timeout=10)
        json_data = r.json()
        if json_data['stat'] != 'OK':
            return "查無資料"
        last = json_data['data'][-1]
        return (f"股票代號：{stock_no}\n日期：{last[0]}\n開盤：{last[3]}\n最高：{last[4]}\n"
                f"最低：{last[5]}\n收盤：{last[6]}\n成交量：{last[1]}")
    except:
        return "取得資料失敗"
