import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

def plot_kline(df: pd.DataFrame, stock_no: str, filepath: str, show_sma=False):
    # ✅ 防呆：檢查資料
    if df.empty:
        raise ValueError("輸入的資料集為空")

    # ✅ 設定中文字體（Render 上請確認字體檔案存在）
    font_path = 'static/fonts/NotoSansTC-Regular.ttf'
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"找不到字體檔案：{font_path}")
    prop = font_manager.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()

    # ✅ 清理與標準化欄位
    df = df.copy()
    df.set_index('日期', inplace=True)
    df.rename(columns={
        '開盤價': 'Open',
        '最高價': 'High',
        '最低價': 'Low',
        '收盤價': 'Close',
        '成交量': 'Volume'
    }, inplace=True)

    # ✅ 樣式設定（紅漲綠跌）
    mc = mpf.make_marketcolors(
        up='red', down='green',
        edge='inherit', wick='inherit', volume='inherit'
    )
    s = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=mc)

    # ✅ 繪圖與儲存
    mpf.plot(
        df,
        type='candle',
        mav=(10, 30) if show_sma else (),
        volume=True,
        title=f"{stock_no} K 線圖（{len(df)} 日）",
        style=s,
        savefig=dict(fname=filepath, dpi=100, bbox_inches='tight'),
        datetime_format='%Y-%m-%d',
        xrotation=15,
        tight_layout=True
    )
