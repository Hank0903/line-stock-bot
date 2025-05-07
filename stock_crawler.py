import requests
import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import mplfinance as mpf
from utils import get_recent_trading_days, date_to_query_format

# 設定圖片輸出資料夾與網址（你需要將這資料夾掛上 CDN 或 imgur 上傳）
IMAGE_OUTPUT_FOLDER = 'static'
IMAGE_HOST_URL = 'https://line-stock-bot-iwcn.onrender.com/static'

# 確保資料夾存在
os.makedirs(IMAGE_OUTPUT_FOLDER, exist_ok=True)

# 設定中文字體
font_path = 'static/fonts/NotoSansTC-Regular.ttf'  # 可以更換為微軟正黑體或其他字型
prop = fm.FontProperties(fname=font_path)

def plot_kline(df: pd.DataFrame, stock_no: str, filepath: str, show_sma=False):
    # 設定中文字體（Render 環境請確保字體存在於該路徑）
    font_path = 'static/fonts/NotoSansTC-Regular.ttf'  # 相對專案目錄的路徑
    prop = font_manager.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()

    df = df.copy()
    df.set_index('日期', inplace=True)

    df.rename(columns={
        '開盤價': 'Open',
        '最高價': 'High',
        '最低價': 'Low',
        '收盤價': 'Close',
        '成交量': 'Volume'
    }, inplace=True)

    mc = mpf.make_marketcolors(
        up='red', down='green', edge='inherit', wick='inherit', volume='inherit')
    s = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=mc)

    mpf.plot(
        df,
        type='candle',
        mav=(10, 30) if show_sma else (),
        volume=True,
        title=f"{stock_no} K 線圖 (近 {len(df)} 日)",
        style=s,
        savefig=filepath
    )

def generate_kline_image(stock_no: str, days: int = 30, show_sma=False):
    df = get_stock_data(stock_no, days)
    if df.empty:
        raise Exception("無法取得資料")

    filename = f"{stock_no}_kline.png"
    filepath = os.path.join(IMAGE_OUTPUT_FOLDER, filename)
    plot_kline(df, stock_no, filepath, show_sma)
    return filename

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

    # 繪製K線圖
    mpf.plot(
        df,
        type='candle',
        mav=(10, 30) if show_sma else (),
        volume=True,
        title=f"{stock_no} K 線圖 (近 {len(df)} 日)",
        style=s,
        savefig=filepath,
       
    )

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
