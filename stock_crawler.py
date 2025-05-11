import re
import requests
import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import mplfinance as mpf
from utils import get_recent_trading_days, date_to_query_format

# 設定圖片輸出資料夾與網址
IMAGE_OUTPUT_FOLDER = 'static'
IMAGE_HOST_URL = 'https://line-stock-bot-iwcn.onrender.com/static'

os.makedirs(IMAGE_OUTPUT_FOLDER, exist_ok=True)

# 設定中文字體
font_path = 'static/fonts/NotoSansTC-Regular.ttf'
prop = fm.FontProperties(fname=font_path)

# 取得區間內所有交易日
def get_trading_days_between(start_date: str, end_date: str)->list[datetime.datetime]:
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    days = []
    while start <= end:
        if start.weekday() < 5:  # 排除週末
            days.append(start)
        start += datetime.timedelta(days=1)
    return days

# 抓取股價資料

def get_stock_data(stock_no: str, days: int = 30):
    dates = get_recent_trading_days(days)
    print(f'dates: {len(dates)}')
    return fetch_stock_data(stock_no, dates)

# 區間抓資料

def get_stock_data_by_date(stock_no: str, start: str, end: str):
    dates = get_trading_days_between(start, end)
    return fetch_stock_data(stock_no, dates)

# 共用資料抓取邏輯

def fetch_stock_data(stock_no: str, dates):
    data = []
    print(f'days: {len(dates)}')

    for date in dates:
        date_param = date_to_query_format(date)
        print(f'dateparam: {date_param}')
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date_param}&stockNo={stock_no}"
        try:
            r = requests.get(url, verify=False, timeout=10)
            json_data = r.json()
            if json_data['stat'] != 'OK':
                continue
            for row in json_data['data']:
                roc_date = row[0]
                parts = roc_date.split('/')
                if len(parts[0]) == 3:
                    parts[0] = str(int(parts[0]) + 1911)
                date_fmt = '-'.join(parts)
                parsed = datetime.datetime.strptime(date_fmt, '%Y-%m-%d')
                data.append({
                    "日期": parsed,
                    "開盤價": float(row[3].replace(',', '')),
                    "最高價": float(row[4].replace(',', '')),
                    "最低價": float(row[5].replace(',', '')),
                    "收盤價": float(row[6].replace(',', '')),
                    "成交量": float(row[1].replace(',', '')),
                })
        except Exception as e:
            print(f"錯誤: {e}")
            continue
    
    # now we have proof of repetition
    print(f'天數 : {len(data)}')    

    df = pd.DataFrame(data)
    df = df.sort_values("日期")
    return df

# 產生 K 線圖（固定天數）
def generate_kline_image(stock_no: str, days: int = 30, show_sma=False):
    df = get_stock_data(stock_no, days)
    print(f'days inside kline{df}')
    if df.empty:
        raise Exception("無法取得資料")
    filename = f"{stock_no}_kline.jpg"
    filepath = os.path.join(IMAGE_OUTPUT_FOLDER, filename)
    plot_kline(df, stock_no, filepath, show_sma)
    return filename

# 產生 K 線圖（日期範圍）
def generate_kline_image_by_date(stock_no: str, start: str, end: str, show_sma=False):
    df = get_stock_data_by_date(stock_no, start, end)
    if df.empty:
        raise Exception("無法取得資料")
    filename = f"{stock_no}_{start}_to_{end}.jpg"
    filepath = os.path.join(IMAGE_OUTPUT_FOLDER, filename)
    plot_kline(df, stock_no, filepath, show_sma)
    return filename

# 繪製K線圖

def plot_kline(df: pd.DataFrame, stock_no: str, filepath: str, show_sma=False):
    #'''
    df = df.copy()
    df.set_index('日期', inplace=True)

    df.rename(columns={
        '開盤價': 'Open',
        '最高價': 'High',
        '最低價': 'Low',
        '收盤價': 'Close',
        '成交量': 'Volume'
    }, inplace=True)
    #'''

    '''
    sample
    ix = pd.DatetimeIndex(['2021-10-11','2021-10-12','2021-10-13','2021-10-14','2021-10-15'])
    df = pd.DataFrame(dict(  Open=[131.4, 131.9, 132.0, 130.9, 131.6],
                         High=[133.2, 132.7, 133.2, 132.7, 131.8],
                          Low=[131.3, 131.3, 131.5, 130.6, 130.7],
                        Close=[132.1, 131.4, 131.8, 132.1, 131.0],
                       Volume=[19591, 21467, 20406, 22611, 22001]),
                       index = ix
                  )
    '''

    # input source has repetition
    df = df[::5]
    mc = mpf.make_marketcolors(up='red', down='green', edge='inherit', wick='inherit', volume='inherit')
    s = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=mc)

    mpf.plot(
        df,
        type='candle',
        mav=(10, 30) if show_sma else (),
        volume=True,
        #title=f"{stock_no} K 線圖 (共 {len(df)} 日)",
        title=f"{stock_no} K line graph (Total {len(df)} days)",
        style=s,
        savefig=dict(fname=filepath, dpi=100, bbox_inches='tight'),
        datetime_format='%b %d',
        xrotation=15,
        tight_layout=True
    )

# 查詢即時資訊

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

