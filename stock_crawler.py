# stock_crawler.py
import requests
import datetime
import os
import pandas as pd
import plotter
from utils import get_recent_trading_days, date_to_query_format

# 設定圖片輸出資料夾與網址（你需要將這資料夾掛上 CDN 或 imgur 上傳）
IMAGE_OUTPUT_FOLDER = 'static'
IMAGE_HOST_URL = 'https://your-image-host.com/static'  # 更換為你的圖床網址

# 確保資料夾存在
os.makedirs(IMAGE_OUTPUT_FOLDER, exist_ok=True)

def get_stock_data(stock_no: str, days: int = 30):
    dates = get_recent_trading_days(days)
    data = []
    for date in dates:
        date_param = date_to_query_format(date)
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
    df = pd.DataFrame(data)
    df = df.sort_values("日期")
    return df

def generate_kline_image(stock_no: str, show_sma=False):
    df = get_stock_data(stock_no)
    if df.empty:
        raise Exception("無法取得資料")

    filename = f"{stock_no}_kline.png"
    filepath = os.path.join(IMAGE_OUTPUT_FOLDER, filename)
    plotter.plot_kline(df, stock_no, filepath, show_sma=show_sma)
    return filename

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

IMAGE_HOST_URL = IMAGE_HOST_URL
