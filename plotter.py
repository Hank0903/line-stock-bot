import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

def plot_kline(df: pd.DataFrame, stock_no: str, filepath: str, show_sma=False):
    # ✅ 設定中文字體（Render 與本機皆通用）
    font_path = 'static/fonts/NotoSansTC-Regular.ttf'
    if os.path.exists(font_path):
        prop = font_manager.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
    else:
        print("⚠️ 找不到中文字體，請確認字體路徑正確！")

    df = df.copy()
    df.set_index('日期', inplace=True)
    df.rename(columns={
        '開盤價': 'Open',
        '最高價': 'High',
        '最低價': 'Low',
        '收盤價': 'Close',
        '成交量': 'Volume'
    }, inplace=True)

    # ✅ 風格與顏色設定
    mc = mpf.make_marketcolors(up='red', down='green', edge='black', wick='black', volume='blue')
    s = mpf.make_mpf_style(base_mpf_style='classic', marketcolors=mc)

    # ✅ 標題
    chart_title = f"{stock_no} K 線圖"

    # ✅ 自訂圖表
    fig, axes = mpf.plot(
        df,
        type='candle',
        mav=(5, 10) if show_sma else (),
        volume=True,
        style=s,
        title=chart_title,
        ylabel='價格',
        ylabel_lower='成交量',
        datetime_format='%m-%d',
        xrotation=20,
        tight_layout=True,
        figratio=(12, 6),
        figscale=2.0,
        returnfig=True
    )

    # ✅ 加上來源註記
    fig.text(0.9, 0.02, "資料來源：TWSE", fontsize=10, ha='right')

    # ✅ 儲存與清理
    fig.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)
