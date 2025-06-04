import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

def plot_kline(df: pd.DataFrame, stock_no: str, filepath: str, show_sma=False):
    # ✅ 設定中文字體（Render 與本機皆通用）
    font_path = 'static/fonts/NotoSansTC-Regular.ttf'
    if not os.path.exists(font_path):
        print("⚠️ 找不到中文字體，請確認字體路徑正確！")
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

    mc = mpf.make_marketcolors(up='red', down='green', edge='inherit', wick='inherit', volume='inherit')
    s = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=mc)

    fig, axlist = mpf.plot(
        df,
        type='candle',
        mav=(10, 30) if show_sma else (),
        volume=True,
        style=s,
        title=f"{stock_no} K 線圖（共 {len(df)} 日）",
        figratio=(18, 5),
        figscale=2.2,
        datetime_format='%m-%d',
        xrotation=20,
        tight_layout=True,
        returnfig=True
    )

    fig.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)
