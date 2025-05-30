import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager

def plot_kline(df: pd.DataFrame, stock_no: str, filepath: str, show_sma=False):
    # 設定中文字體（Render 環境請確保字體存在於該路徑）
    font_path = 'static/fonts/NotoSansTC-Regular.ttf'
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

    mpf.plot(
        df,
        type='candle',
        mav=(10, 30) if show_sma else (),
        volume=True,
        title=f"{stock_no} Kline（ {len(df)} days）",
        style=s,
        savefig=dict(fname=filepath, dpi=100, bbox_inches='tight'),
        datetime_format='%Y-%m-%d',
        xrotation=15,
        tight_layout=True
    )
