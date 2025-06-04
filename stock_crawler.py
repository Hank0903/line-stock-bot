import requests
import datetime
import os
import pandas as pd
from plotter import plot_kline
from utils import get_recent_trading_days, get_trading_days_between, date_to_query_format

# 設定圖片輸出資料夾與網址（你需要將這資料夾掛上 CDN 或 imgur 上傳）
IMAGE_OUTPUT_FOLDER = 'static'
IMAGE_HOST_URL = 'https://line-stock-bot-iwcn.onrender.com/static'

# 確保資料夾存在
os.makedirs(IMAGE_OUTPUT_FOLDER, exist_ok=True)


# ✅ 爬取日資料
def get_stock_data(stock_no: str, days: int = 30):
    dates = get_recent_trading_days(days)
    return fetch_stock_data(stock_no, dates)

# ✅ 爬取特定區間資料
def get_stock_data_by_date(stock_no: str, start: str, end: str):
    dates = get_trading_days_between(start, end)
    return fetch_stock_data(stock_no, dates)

# ✅ 核心爬蟲邏輯
def fetch_stock_data(stock_no: str, dates):
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
            print(f"[❌ 錯誤] 下載 {stock_no} @ {date_param} 時失敗：{e}")
            continue
    df = pd.DataFrame(data)
    df = df.sort_values("日期")
    return df

# ✅ 即時價格查詢
def get_realtime_price(stock_no: str):
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_no}.tw"
    try:
        r = requests.get(url, verify=False, timeout=10)
        json_data = r.json()
        if not json_data['msgArray']:
            return "查無即時報價"
        item = json_data['msgArray'][0]
        return (f"📈 股票代號：{item['c']}\n"
                f"📛 名稱：{item['n']}\n"
                f"💰 最新成交價：{item['z']}\n"
                f"📊 開盤：{item['o']}\n"
                f"📈 最高：{item['h']}\n"
                f"📉 最低：{item['l']}\n"
                f"📦 成交量：{item['v']}")
    except:
        return "❌ 即時報價查詢失敗"

# ✅ 股價摘要（來自某一日）
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

# ✅ K 線圖產生（依天數）
def generate_kline_image(stock_no: str, days: int = 30):
    df = get_stock_data(stock_no, days)
    if df.empty:
        raise Exception("無法取得資料")
    filename = f"{stock_no}_kline.png"
    filepath = os.path.join(IMAGE_OUTPUT_FOLDER, filename)
    plot_kline(df, stock_no, filepath)
    return filename

# ✅ K 線圖產生（指定區間）
def generate_kline_image_by_date(stock_no: str, start: str, end: str):
    df = get_stock_data_by_date(stock_no, start, end)
    if df.empty:
        raise Exception("無法取得資料")
    filename = f"{stock_no}_{start}_to_{end}.png"
    filepath = os.path.join(IMAGE_OUTPUT_FOLDER, filename)
    plot_kline(df, stock_no, filepath)
    return filename




# 公開變數
__all__ = [
    'IMAGE_HOST_URL',
    'generate_kline_image',
    'generate_kline_image_by_date',
    'get_stock_info',
    'get_realtime_price'
]
